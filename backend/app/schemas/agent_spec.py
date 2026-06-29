from __future__ import annotations

from enum import Enum

from pydantic import Field, model_validator

from app.schemas.common import AutonomyLevel, StrictBaseModel, Timestamped, TriggerSpec
from app.schemas.tool import ToolPermission


class AgentStatus(str, Enum):
    idle = "idle"
    running = "running"
    waiting_approval = "waiting_approval"
    blocked = "blocked"
    disabled = "disabled"
    error = "error"
    active = "active"


class MemoryPolicy(StrictBaseModel):
    read: list[str] = Field(default_factory=list)
    write: list[str] = Field(default_factory=list)
    require_source: bool = True
    low_confidence_requires_review: bool = True


class ActionPolicy(StrictBaseModel):
    auto: list[str] = Field(default_factory=list)
    approval_required: list[str] = Field(default_factory=list)


class ToolBinding(StrictBaseModel):
    tool_id: str = Field(min_length=1)
    permission: ToolPermission | None = None
    enabled: bool = True


class EvaluationRule(str, Enum):
    source_required = "source_required"
    relevance_score_required = "relevance_score_required"
    duplication_check = "duplication_check"
    confidence_required = "confidence_required"
    audit_log_required = "audit_log_required"


class AgentSpec(Timestamped):
    agent_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    role: str = Field(min_length=1)
    mission: str = Field(min_length=1)
    status: AgentStatus = AgentStatus.idle
    autonomy_level: AutonomyLevel = AutonomyLevel.L1
    project_ids: list[str] = Field(default_factory=list)
    triggers: list[TriggerSpec] = Field(default_factory=list)
    tools: list[ToolBinding] = Field(default_factory=list)
    memory_access: MemoryPolicy = Field(default_factory=MemoryPolicy)
    actions: ActionPolicy = Field(default_factory=ActionPolicy)
    evaluation: list[EvaluationRule] = Field(default_factory=list)
    output_format: str = "markdown"
    failure_policy: str = "record_error_and_stop"
    version: str = "0.1.0"

    @model_validator(mode="after")
    def validate_l4_not_default(self) -> "AgentSpec":
        if self.autonomy_level == AutonomyLevel.L4:
            raise ValueError("L4 autonomy is not enabled in Phase 0/MVP")
        return self
