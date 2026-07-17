from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from app.agent_runtime.cognition.planner import PlanDecision, Planner
from app.schemas.agent_spec import AgentSpec
from app.schemas.memory import MemoryItem
from app.schemas.task import TaskSpec


class WakeupLoop:
    """Build one heartbeat observation and ask the planner for work."""

    def __init__(self, planner: Planner | None = None) -> None:
        self.planner = planner or Planner()

    def observe(
        self,
        agent: AgentSpec,
        recent_tasks: Sequence[TaskSpec] | None = None,
        recent_memory: Sequence[MemoryItem] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        observation = {
            "agent_id": agent.agent_id,
            "mission": agent.mission,
            "recent_tasks": list(recent_tasks or []),
            "recent_memory": list(recent_memory or []),
        }
        observation.update(context or {})
        return observation

    def observe_and_decide(
        self,
        agent: AgentSpec,
        recent_tasks: Sequence[TaskSpec] | None = None,
        recent_memory: Sequence[MemoryItem] | None = None,
        context: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], PlanDecision]:
        observation = self.observe(agent, recent_tasks, recent_memory, context)
        return observation, self.planner.decide(agent, observation)

    def observe_and_plan(
        self,
        agent: AgentSpec,
        recent_tasks: Sequence[TaskSpec] | None = None,
        recent_memory: Sequence[MemoryItem] | None = None,
    ) -> tuple[dict[str, Any], list[TaskSpec]]:
        observation, decision = self.observe_and_decide(
            agent,
            recent_tasks=recent_tasks,
            recent_memory=recent_memory,
        )
        return observation, decision.tasks
