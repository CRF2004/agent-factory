from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from app.agent_runtime.lifecycle.heartbeat import HeartbeatService
from app.agent_runtime.runtime import AutonomousRuntime
from app.schemas.agent_spec import AgentSpec
from app.schemas.heartbeat import HeartbeatAction
from app.schemas.memory import MemoryType
from app.services.repository import InMemoryRepository
from app.services.runtime import RuntimeService
from app.services.vector_store import NoopVectorStore
from app.services.web_search import MockWebSearchProvider


class MutableClock:
    def __init__(self, value: datetime) -> None:
        self.value = value

    def __call__(self) -> datetime:
        return self.value

    def advance(self, seconds: int) -> None:
        self.value += timedelta(seconds=seconds)


class JsonLLMClient:
    def chat(self, model=None, messages=None, **kwargs):
        return {
            "content": json.dumps(
                {
                    "summary": "Focused medical AI update.",
                    "relevance_score": 0.8,
                    "novelty_score": 0.7,
                    "key_findings": ["Use focused disease and modality queries."],
                }
            )
        }

    def embed(self, texts, model=None):
        return [[0.0] * 8 for _ in texts]


def build_service(
    repository: InMemoryRepository,
    clock: MutableClock,
) -> HeartbeatService:
    task_runtime = RuntimeService(
        repository=repository,
        llm_client=JsonLLMClient(),
        web_search=MockWebSearchProvider(),
        vector_store=NoopVectorStore(),
    )
    return HeartbeatService(
        repository=repository,
        autonomous_runtime=AutonomousRuntime(repository, task_runtime),
        default_wakeup_seconds=3600,
        lease_seconds=300,
        clock=clock,
    )


def create_research_agent(repository: InMemoryRepository) -> AgentSpec:
    agent = AgentSpec(
        agent_id="research-agent",
        name="Research Agent",
        role="researcher",
        mission="Track latest medical AI research",
    )
    repository.create_agent(agent)
    return agent


def test_heartbeat_executes_then_respects_cooldown() -> None:
    repository = InMemoryRepository()
    agent = create_research_agent(repository)
    clock = MutableClock(datetime(2026, 7, 17, 9, 0, tzinfo=UTC))
    service = build_service(repository, clock)

    first = service.run_agent(agent.agent_id)
    second = service.run_agent(agent.agent_id)

    assert first.action == HeartbeatAction.task_created
    assert first.task is not None
    assert first.state.last_task_id == first.task.task_id
    assert first.state.next_wakeup_at is not None
    assert second.action == HeartbeatAction.no_action
    assert second.reason == "mission handled within cooldown"
    assert len(repository.list_tasks()) == 1


def test_heartbeat_lease_prevents_duplicate_execution() -> None:
    repository = InMemoryRepository()
    agent = create_research_agent(repository)
    now = datetime(2026, 7, 17, 9, 0, tzinfo=UTC)
    clock = MutableClock(now)
    service = build_service(repository, clock)

    repository.acquire_heartbeat_lease(
        agent_id=agent.agent_id,
        lease_token="held-lease",
        now=now.isoformat(),
        lease_until=(now + timedelta(minutes=5)).isoformat(),
    )

    result = service.run_agent(agent.agent_id)

    assert result.action == HeartbeatAction.already_running
    assert repository.list_tasks() == []


def test_due_runner_executes_only_due_agents() -> None:
    repository = InMemoryRepository()
    due_agent = create_research_agent(repository)
    future_agent = AgentSpec(
        agent_id="future-agent",
        name="Future Agent",
        role="researcher",
        mission="Track future research",
    )
    repository.create_agent(future_agent)
    clock = MutableClock(datetime(2026, 7, 17, 9, 0, tzinfo=UTC))
    service = build_service(repository, clock)
    future_state = service.get_state(future_agent.agent_id)
    future_state.next_wakeup_at = (clock() + timedelta(hours=1)).isoformat()
    repository.upsert_heartbeat_state(future_state)

    result = service.run_due_agents()

    assert result.checked_agents == 2
    assert result.due_agents == 1
    assert result.results[0].agent_id == due_agent.agent_id


def test_reflection_updates_existing_experience() -> None:
    repository = InMemoryRepository()
    agent = create_research_agent(repository)
    clock = MutableClock(datetime(2026, 7, 17, 9, 0, tzinfo=UTC))
    service = build_service(repository, clock)

    first = service.run_agent(agent.agent_id)
    clock.advance(10)
    second = service.run_agent(agent.agent_id, force=True)

    experiences = [
        memory
        for memory in repository.list_memory_items()
        if memory.type == MemoryType.experience
    ]
    assert first.experience_memory is not None
    assert second.experience_memory is not None
    assert len(experiences) == 1
    assert experiences[0].source_task_id == second.task.task_id
