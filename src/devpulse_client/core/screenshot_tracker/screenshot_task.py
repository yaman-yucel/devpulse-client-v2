from __future__ import annotations

from dataclasses import dataclass

from .screenshot_capturer import ScreenshotCapturer


@dataclass
class ScreenshotTask:
  

    interval: int
    capturer: ScreenshotCapturer
    _last: float | None = None

    def tick(self, now: float) -> None:
      
        if self._last is None or now - self._last >= self.interval:
            self._last = now
            self.capturer.capture_all_monitors()
