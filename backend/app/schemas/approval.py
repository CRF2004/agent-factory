from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from app.schemas.common import Timestamped
from app.schemas.tool import RiskLevel


class ApprovalStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    needs_revision = "needs_revision"
    expired = "expired"


class ApprovalRequest(Timestamped):
    approval_id: str = Field(min_length=1)
    requesting_agent: str = Field(min_length=1)
    task_id: str | None = None
    action_type: str = Field(min_length=1)
    risk_level: RiskLevel
    summary: str = Field(min_length=1)
    details: dict[str, Any] = Field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.pending
    user_decision: str | None = None
    decided_at: str | None = None
