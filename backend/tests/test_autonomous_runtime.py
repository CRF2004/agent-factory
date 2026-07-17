from __future__ import annotations

import json

from app.agent_runtime.runtime import AutonomousRuntime
from app.schemas.agent_spec import AgentSpec
from app.schemas.memory import MemoryType
from app.schemas.run import RunStatus
from app.schemas.task import TaskSpec, TaskStatus, TaskType
from app.services.repository import InMemoryRepository
from app.services.runtime import RuntimeService
from app.services.vector_store import NoopVectorStore
from app.services.web_search import MockWebSearchProvider


class JsonLLMClient:
    def chat(self, model=None, messages=None, **kwargs):
        return {
            "content": json.dumps(
                {
                    "summary": "Focused medical AI update.",
                    "relevance_score": 0.8,
                    "novelty_score": 0.7,
                    "key_findings": ["Use focused disease + modality queries."],
                }
            )
        }

    def embed(self, texts, model=None):
        return [[0.0] * 8 for _ in texts]


def build_runtime(repository: InMemoryRepository) -> AutonomousRuntime:
    task_runtime = RuntimeService(
        repository=repository,
        llm_client=JsonLLMClient(),
        web_search=MockWebSearchProvider(),
        vector_store=NoopVectorStore(),
    )
    return AutonomousRuntime(repository, task_runtime)


def test_autonomous_cycle_creates_executes_and_reflects() -> None:
    repository = InMemoryRepository()
    agent = AgentSpec(
        agent_id="research-agent",
        name="Research Agent",
        role="researcher",
        mission="Track latest medical AI research",
    )
    repository.create_agent(agent)

    result = build_runtime(repository).run_once(agent.agent_id)

    assert result.acted
    assert result.executed_task is not None
    assert result.executed_task.status == TaskStatus.completed
    assert result.run is not None
    assert result.run.status == RunStatus.completed
    assert result.experience_memory is not None
    assert result.experience_memory.type == MemoryType.experience
    assert result.experience_memory.source_task_id == result.executed_task.task_id
    assert result.experience_memory.source_run_id == result.run.id

    memories = repository.list_memory_items()
    assert any(memory.type == MemoryType.knowledge for memory in memories)
    assert any(memory.type == MemoryType.experience for memory in memories)


def test_autonomous_cycle_does_not_duplicate_active_work() -> None:
    repository = InMemoryRepository()
    agent = AgentSpec(
        agent_id="research-agent",
        name="Research Agent",
        role="researcher",
        mission="Track latest medical AI research",
    )
    repository.create_agent(agent)
    repository.create_task(
        TaskSpec(
            task_id="task-active",
            title="Existing scan",
            type=TaskType.research_scan,
            owner_agent=agent.agent_id,
            status=TaskStatus.queued,
        )
    )

    result = build_runtime(repository).run_once(agent.agent_id)

    assert not result.acted
    assert result.planned_tasks == []
    assert len(repository.list_tasks()) == 1
    assert not any(
        memory.type == MemoryType.experience
        for memory in repository.list_memory_items()
    )
