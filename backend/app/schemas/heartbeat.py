from __future__ import annotations

from enum import Enum

from pydantic import Field

from app.schemas.common import StrictBaseModel, Timestamped
from app.schemas.memory import MemoryItem
from app.schemas.run import AgentRun
from app.schemas.task import TaskSpec


class HeartbeatAction(str, Enum):
    task_created = "task_created"
    no_action = "no_action"
    already_running = "already_running"
    disabled = "disabled"
    error = "error"


class AgentHeartbeatState(Timestamped):
    agent_id: str = Field(min_length=1)
    last_wakeup_at: str | None = None
    last_action_at: str | None = None
    next_wakeup_at: str | None = None
    last_task_id: str | None = None
    lease_token: str | None = None
    lease_until: str | None = None
    consecutive_failures: int = Field(default=0, ge=0)
    last_error: str | None = None


class HeartbeatRunResult(StrictBaseModel):
    agent_id: str
    action: HeartbeatAction
    reason: str
    state: AgentHeartbeatState
    task: TaskSpec | None = None
    run: AgentRun | None = None
    experience_memory: MemoryItem | None = None


class RunDueHeartbeatsResult(StrictBaseModel):
    checked_agents: int
    due_agents: int
    results: list[HeartbeatRunResult] = Field(default_factory=list)
