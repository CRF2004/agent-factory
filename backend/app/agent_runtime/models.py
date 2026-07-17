from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AgentSpec:
    name: str
    role: str
    goals: list[str]
    proactive_level: int = 1
    tools: list[str] = field(default_factory=list)


@dataclass
class AgentMemory:
    kind: str
    content: str
    confidence: float = 0.5
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentTask:
    task_type: str
    description: str
    priority: str = "normal"
    status: str = "created"
    metadata: dict[str, Any] = field(default_factory=dict)
