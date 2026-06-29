from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from app.schemas.common import Timestamped
from app.schemas.tool import RiskLevel


class RunStatus(str, Enum):
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class ToolCallStatus(str, Enum):
    started = "started"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"


class AgentRun(Timestamped):
    id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    status: RunStatus
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    started_at: str
    ended_at: str | None = None
    error_message: str | None = None
    cost: float | None = None


class ToolCall(Timestamped):
    id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    tool_id: str = Field(min_length=1)
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    status: ToolCallStatus
    risk_level: RiskLevel = RiskLevel.low
