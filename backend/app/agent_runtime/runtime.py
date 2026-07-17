from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.agent_runtime.cognition.reflection import ReflectionEngine
from app.agent_runtime.lifecycle.wakeup import WakeupLoop
from app.schemas.agent_spec import AgentStatus
from app.schemas.memory import MemoryItem
from app.schemas.run import AgentRun
from app.schemas.task import TaskSpec
from app.services.repository import Repository
from app.services.runtime import RuntimeService


@dataclass(frozen=True)
class AutonomousCycleResult:
    agent_id: str
    observation: dict[str, Any]
    planned_tasks: list[TaskSpec] = field(default_factory=list)
    executed_task: TaskSpec | None = None
    run: AgentRun | None = None
    experience_memory: MemoryItem | None = None
    decision_reason: str = ""
    next_wakeup_seconds: int = 3600

    @property
    def acted(self) -> bool:
        return self.run is not None


class AutonomousRuntime:
    """Orchestrate one safe autonomous heartbeat on top of RuntimeService."""

    def __init__(
        self,
        repository: Repository,
        runtime_service: RuntimeService,
        wakeup_loop: WakeupLoop | None = None,
        reflection_engine: ReflectionEngine | None = None,
    ) -> None:
        self.repository = repository
        self.runtime_service = runtime_service
        self.wakeup_loop = wakeup_loop or WakeupLoop()
        self.reflection_engine = reflection_engine or ReflectionEngine(repository)

    def run_once(
        self,
        agent_id: str,
        context: dict[str, Any] | None = None,
    ) -> AutonomousCycleResult:
        agent = self.repository.get_agent(agent_id)
        if agent.status == AgentStatus.disabled:
            return AutonomousCycleResult(
                agent_id=agent_id,
                observation={"agent_id": agent_id, "disabled": True},
                decision_reason="agent disabled",
            )

        recent_tasks = [
            task
            for task in self.repository.list_tasks()
            if task.owner_agent == agent_id
        ][-20:]
        recent_memory = [
            item
            for item in self.repository.list_memory_items()
            if item.created_by_agent_id == agent_id
        ][-10:]

        observation, decision = self.wakeup_loop.observe_and_decide(
            agent,
            recent_tasks=recent_tasks,
            recent_memory=recent_memory,
            context=context,
        )
        if not decision.tasks:
            agent.status = AgentStatus.idle
            self.repository.upsert_agent(agent)
            return AutonomousCycleResult(
                agent_id=agent_id,
                observation=observation,
                decision_reason=decision.reason,
                next_wakeup_seconds=decision.next_wakeup_seconds,
            )

        task = decision.tasks[0]
        agent.status = AgentStatus.running
        self.repository.upsert_agent(agent)

        try:
            self.repository.create_task(task)
            run = self.runtime_service.run_task(task.task_id)
            completed_task = self.repository.get_task(task.task_id)
            experience = self.reflection_engine.reflect(agent, completed_task, run)
        except Exception:
            agent.status = AgentStatus.error
            self.repository.upsert_agent(agent)
            raise

        agent.status = AgentStatus.idle
        self.repository.upsert_agent(agent)
        return AutonomousCycleResult(
            agent_id=agent_id,
            observation=observation,
            planned_tasks=decision.tasks,
            executed_task=completed_task,
            run=run,
            experience_memory=experience,
            decision_reason=decision.reason,
            next_wakeup_seconds=decision.next_wakeup_seconds,
        )
