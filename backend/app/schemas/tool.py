from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from app.schemas.common import StrictBaseModel, Timestamped


class ToolType(str, Enum):
    information = "information"
    file = "file"
    code = "code"
    data = "data"
    external_action = "external_action"
    memory = "memory"
    llm = "llm"


class ToolPermission(str, Enum):
    read_only = "read_only"
    write_local = "write_local"
    write_memory = "write_memory"
    write_external = "write_external"
    dangerous = "dangerous"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ToolSpec(Timestamped):
    tool_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    type: ToolType
    description: str = ""
    permission: ToolPermission
    risk_level: RiskLevel = RiskLevel.low
    requires_approval: bool = False
    allowed_agents: list[str] = Field(default_factory=list)
    config_schema: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
