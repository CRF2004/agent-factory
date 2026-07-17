from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from app.schemas.agent_spec import AgentSpec
from app.schemas.task import TaskSpec, TaskStatus, TaskType


ACTIVE_TASK_STATES = {
    TaskStatus.created,
    TaskStatus.queued,
    TaskStatus.running,
    TaskStatus.waiting_approval,
    TaskStatus.blocked,
}


@dataclass(frozen=True)
class PlanDecision:
    reason: str
    tasks: list[TaskSpec] = field(default_factory=list)
    next_wakeup_seconds: int = 3600

    @property
    def should_act(self) -> bool:
        return bool(self.tasks)


class Planner:
    """Translate an observation into tasks executable by RuntimeService."""

    def decide(
        self,
        agent: AgentSpec,
        observation: dict[str, Any],
    ) -> PlanDecision:
        default_wakeup_seconds = max(
            1,
            int(observation.get("default_wakeup_seconds", 3600)),
        )
        tasks = observation.get("recent_tasks", [])
        active_tasks = [task for task in tasks if task.status in ACTIVE_TASK_STATES]
        if active_tasks:
            return PlanDecision(
                reason="active task exists",
                next_wakeup_seconds=min(60, default_wakeup_seconds),
            )

        if observation.get("cooldown_active"):
            return PlanDecision(
                reason="mission handled within cooldown",
                next_wakeup_seconds=max(
                    1,
                    int(
                        observation.get(
                            "cooldown_remaining_seconds",
                            default_wakeup_seconds,
                        )
                    ),
                ),
            )

        mission = agent.mission.strip()
        task = TaskSpec(
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
        return PlanDecision(
            reason="no active or recent equivalent task",
            tasks=[task],
            next_wakeup_seconds=default_wakeup_seconds,
        )

    def create_plan(
        self,
        agent: AgentSpec,
        observation: dict[str, Any],
    ) -> list[TaskSpec]:
        return self.decide(agent, observation).tasks
