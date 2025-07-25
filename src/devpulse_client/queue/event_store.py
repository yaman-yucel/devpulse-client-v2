from __future__ import annotations


from collections import deque
from dataclasses import dataclass, asdict
from typing import Deque, Dict, Any, List
from datetime import datetime, timedelta

from devpulse_client.config.tracker_config import tracker_settings
from devpulse_client.tables.activity_table import ActivityEventType


@dataclass(slots=True)
class _ActivityEvent:
    username: str
    timestamp: datetime
    event: str


@dataclass(slots=True)
class _HeartbeatEvent:
    username: str
    timestamp: datetime


@dataclass(slots=True)
class _WindowEvent:
    username: str
    timestamp: datetime
    window_title: str
    duration: float
    start_time: datetime
    end_time: datetime | None



class EventStore:
    
    _events: Deque[Dict[str, Any]] = deque() 
    

    @staticmethod
    
    def _push(event_obj: object) -> None:  # noqa: D401 – simple helper
        """Serialise *event_obj* to a dict and push it onto the queue."""
        EventStore._events.append(asdict(event_obj))
        

    @staticmethod
    def log_activity(label: str, timestamp: datetime | None = None) -> None:  # noqa: D401
        """Record an *Activity* event in the queue."""
        ts = timestamp or datetime.now()

        EventStore._push(
            _ActivityEvent(
                username=tracker_settings.user,
                timestamp=ts,
                event=label,
            )
        )

       
    @staticmethod
    def heartbeat(timestamp: datetime | None = None) -> None:
        """Write a HeartbeatEvent row.

        The optional *timestamp* argument allows callers to record a specific
        time rather than the moment this function is invoked. If *timestamp*
        is *None*, the current time (``datetime.now()``) is used for backward
        compatibility.
        """
        ts = timestamp or datetime.now()
        EventStore._push(
            _HeartbeatEvent(
                username=tracker_settings.user,
                timestamp=ts,
            )
        )

    @staticmethod
    def log_window_event(
        window_title: str,
        timestamp: datetime | None = None,
        duration: float = 0.0,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> None:  # noqa: D401
        """Record a *Window* event in the queue.

        This keeps the signature identical to the previous DB implementation so that
        existing call-sites remain unchanged.
        """
        
        # Determine the actual start and end times to use
        if start_time is not None and end_time is not None:
            actual_start_time = start_time
            actual_end_time = end_time
            actual_duration = (end_time - start_time).total_seconds()
            # Use start_time for timestamp field for consistency
            ts = start_time
        else:
            # Fall back to legacy parameters
            ts = timestamp or datetime.now()
            actual_start_time = ts
            actual_end_time = ts + timedelta(seconds=duration) if duration > 0 else None
            actual_duration = duration

        EventStore._push(
            _WindowEvent(
                username=tracker_settings.user,
                timestamp=ts,
                window_title=window_title,
                duration=actual_duration,
                start_time=actual_start_time,
                end_time=actual_end_time,
            )
        )
     # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    @staticmethod
    def get_all_events() -> List[Dict[str, Any]]:
        """Return a *copy* of all events currently in the queue."""
        return list(EventStore._events)

    @staticmethod
    def clear() -> None:
        """Remove all events from the queue (mainly for testing)."""
        EventStore._events.clear()