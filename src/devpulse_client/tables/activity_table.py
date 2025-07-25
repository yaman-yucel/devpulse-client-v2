from datetime import datetime
from enum import StrEnum

class ActivityEventType(StrEnum):
    STARTED = "System Started"
    STOPPED = "System Stopped"
    SCREEN_LOCKED = "Screen Locked"
    SCREEN_UNLOCKED = "Screen Unlocked"
    ACTIVE = "User Active"
    INACTIVE = "User Inactive"
    UNSUPPORTED = "Unsupported Platform"
    SHUTDOWN = "System Shutdown"

