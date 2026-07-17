from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.schemas.agent_spec import AgentSpec
from app.schemas.task import TaskSpec, TaskType


class Planner:
    """Translate an observation into tasks executable by RuntimeService."""

    def create_plan(
        self,
        agent: AgentSpec,
        observation: dict[str, Any],
    ) -> list[TaskSpec]:
        if observation.get("active_tasks"):
            return []

        mission = agent.mission.strip()
        return [
            TaskSpec(
                task_id=f"task_{uuid4().hex}",
                title=f"Autonomous scan: {mission}",
                type=TaskType.research_scan,
                owner_agent=agent.agent_id,
                project_id=agent.project_ids[0] if agent.project_ids else None,
                created_by="autonomous_planner",
                input={"topics": [mission], "sources": ["web"]},
                expected_output=["summary", "key_findings"],
                next_action="execute",
            )
        ]
