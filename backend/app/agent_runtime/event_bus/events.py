from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AgentEvent:
    event_type: str
    source: str
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


RESEARCH_COMPLETED = "research_completed"
TASK_CREATED = "task_created"
TASK_COMPLETED = "task_completed"
MEMORY_CREATED = "memory_created"
