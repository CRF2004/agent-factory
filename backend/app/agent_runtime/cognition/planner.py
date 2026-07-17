from __future__ import annotations

from uuid import uuid4

from app.schemas.task import TaskSpec, TaskType


class Planner:
    """Minimal autonomous planner.

    Converts an agent observation into executable tasks without replacing the
    existing RuntimeService.
    """

    def create_plan(self, agent, observation: dict) -> list[TaskSpec]:
        if observation.get("active_tasks"):
            return []

        mission = agent.mission
        return [
            TaskSpec(
                task_id=f"task_{uuid4().hex}",
                title=f"Autonomous scan: {mission}",
                type=TaskType.research_scan,
                owner_agent=agent.agent_id,
                created_by="autonomous_planner",
                input={"topics": [mission]},
                expected_output=["summary", "key_findings"],
            )
        ]
