from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class AutonomyLevel(str, Enum):
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"


class TriggerType(str, Enum):
    manual = "manual"
    schedule = "schedule"
    event = "event"


class TriggerSpec(StrictBaseModel):
    type: TriggerType
    cron: str | None = None
    event_name: str | None = None
    enabled: bool = True
    input: dict[str, Any] = Field(default_factory=dict)


class Timestamped(StrictBaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None
