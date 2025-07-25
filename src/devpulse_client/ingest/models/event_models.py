from __future__ import annotations

from datetime import datetime
from typing import List, Union, Optional
from pydantic import BaseModel, ConfigDict, Field


class ActivityEvent(BaseModel):
    username: str
    timestamp: datetime
    event: str


class HeartbeatEvent(BaseModel):
    username: str
    timestamp: datetime


class WindowEvent(BaseModel):
    username: str
    timestamp: datetime
    window_title: str
    duration: float
    start_time: datetime
    end_time: datetime | None
    


EventUnion = ActivityEvent|HeartbeatEvent|WindowEvent 


class EventRequest(BaseModel):
   
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid",json_encoders={datetime: lambda v: v.isoformat()},)

    events: list[EventUnion] = Field(..., description="List of events to send to the server.")