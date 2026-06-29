from __future__ import annotations

from enum import Enum

from pydantic import Field

from app.schemas.common import StrictBaseModel, Timestamped


class MemoryType(str, Enum):
    knowledge = "knowledge"
    experience = "experience"
    skill = "skill"


class MemoryStatus(str, Enum):
    candidate = "candidate"
    approved = "approved"
    active = "active"
    deprecated = "deprecated"
    rejected = "rejected"
    conflict = "conflict"


class MemoryItem(Timestamped):
    id: str = Field(min_length=1)
    type: MemoryType
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    summary: str = ""
    source: str | None = None
    source_task_id: str | None = None
    source_run_id: str | None = None
    status: MemoryStatus = MemoryStatus.candidate
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    reliability_score: float | None = Field(default=None, ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)
    related_projects: list[str] = Field(default_factory=list)
    created_by_agent_id: str | None = None


class SkillSpec(Timestamped):
    skill_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    trigger_condition: str = ""
    inputs: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    approval_policy: str = "approval_required_for_external_write"
    version: str = "0.1.0"
    created_from: str | None = None
    last_used_at: str | None = None
