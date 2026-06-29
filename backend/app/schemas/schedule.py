from __future__ import annotations

from typing import Any

from pydantic import Field

from app.schemas.common import Timestamped
from app.schemas.task import TaskType


class ScheduleSpec(Timestamped):
    schedule_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    task_type: TaskType
    cron: str = Field(min_length=1)
    input: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    last_run_at: str | None = None
    next_run_at: str | None = None
