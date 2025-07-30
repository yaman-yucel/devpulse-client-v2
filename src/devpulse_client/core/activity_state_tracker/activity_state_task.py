from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from loguru import logger

from devpulse_client.config.tracker_config import tracker_settings
from devpulse_client.queue.event_store import EventStore
from devpulse_client.tables.activity_table import ActivityEventType

from .idle_detector import IdleDetector
from .screen_lock_detector import ScreenLockDetector
from .screen_locker import lock_screen

@dataclass
class ActivityStateTask:
    _locked: bool | None = None
    _idle: bool | None = None
    _idle_detector: IdleDetector = IdleDetector()
    _lock_detector: ScreenLockDetector = ScreenLockDetector()

    _last_lock_time: datetime = datetime.now()
    
    def tick(self, now: float) -> tuple[bool | None, bool | None]:
        
        timestamp = datetime.now()
        
        locked = self._lock_detector.is_locked()
        
        if (timestamp - self._last_lock_time).total_seconds() >= tracker_settings.LOCK_INTERVAL_SECONDS:
            try:
                lock_screen()
                self._last_lock_time = timestamp
                logger.info("Screen locked by scheduler (based on config interval).")
            except RuntimeError as e:
                logger.error(f"Screen lock failed: {e}")

        
        if self._locked is None:
            if locked:
                state = ActivityEventType.SCREEN_LOCKED
                logger.info(f"Logging activity: {state.value}")
                EventStore.log_activity(state.value, timestamp=timestamp)
                self._locked = True
                self._idle = False
            else:
                idle_seconds = self._idle_detector.seconds_idle()
                is_idle = idle_seconds >= tracker_settings.IDLE_THRESHOLD

                state = ActivityEventType.INACTIVE if is_idle else ActivityEventType.ACTIVE
                logger.info(f"Logging activity: {state.value}")
                EventStore.log_activity(state.value, timestamp=timestamp)

                self._locked = False
                self._idle = is_idle
        else:
            if locked and not self._locked:
                state = ActivityEventType.SCREEN_LOCKED
                logger.info(f"Logging activity: {state.value}")
                EventStore.log_activity(state.value, timestamp=timestamp)
                self._locked, self._idle = True, False
            elif not locked and self._locked:
                state = ActivityEventType.SCREEN_UNLOCKED
                logger.info(f"Logging activity: {state.value}")
                EventStore.log_activity(state.value, timestamp=timestamp)
                self._locked = False
                state = ActivityEventType.ACTIVE
                logger.info(f"Logging activity: {state.value}")
                EventStore.log_activity(state.value, timestamp=timestamp)

        if not locked:
            idle_seconds = self._idle_detector.seconds_idle()
            is_idle = idle_seconds >= tracker_settings.IDLE_THRESHOLD

            if self._idle is not None:
                if is_idle and not self._idle:
                    state = ActivityEventType.INACTIVE
                    logger.info(f"Logging activity: {state.value}")
                    EventStore.log_activity(state.value, timestamp=timestamp)
                    self._idle = True
                elif not is_idle and self._idle:
                    state = ActivityEventType.ACTIVE
                    logger.info(f"Logging activity: {state.value}")
                    EventStore.log_activity(state.value, timestamp=timestamp)
                    self._idle = False

        return self._locked, self._idle
