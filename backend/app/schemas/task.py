from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from app.schemas.common import StrictBaseModel, Timestamped


class TaskStatus(str, Enum):
    created = "created"
    queued = "queued"
    running = "running"
    waiting_approval = "waiting_approval"
    blocked = "blocked"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class TaskType(str, Enum):
    research_scan = "research_scan"
    project_review = "project_review"
    memory_update = "memory_update"
    task_decomposition = "task_decomposition"
    weekly_report = "weekly_report"
    custom = "custom"


class TaskSpec(Timestamped):
    task_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    type: TaskType
    owner_agent: str = Field(min_length=1)
    project_id: str | None = None
    status: TaskStatus = TaskStatus.created
    priority: TaskPriority = TaskPriority.medium
    created_by: str = "manual"
    input: dict[str, Any] = Field(default_factory=dict)
    expected_output: list[str] = Field(default_factory=list)
    output: dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = False
    dependencies: list[str] = Field(default_factory=list)
    next_action: str | None = None
    retry_count: int = 0
