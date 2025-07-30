from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from devpulse_client.queue.event_store import EventStore


@dataclass
class HeartbeatTask:
    

    interval: int
    _last: float | None = None

    def tick(self, now: float) -> None:
        
        if self._last is None or now - self._last >= self.interval:
            self._last = now
            EventStore.heartbeat(timestamp=datetime.fromtimestamp(timestamp=now))
