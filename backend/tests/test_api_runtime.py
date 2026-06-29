from app.main import create_app
from app.schemas.task import TaskSpec, TaskStatus
from app.services.llm_client import MockLLMClient
from app.services.repository import InMemoryRepository
from app.services.runtime import RuntimeService, TaskNotRunnableError
from app.services.vector_store import NoopVectorStore
from app.services.web_search import MockWebSearchProvider
from app.templates.builtin_agents import BUILTIN_AGENT_TEMPLATES


def make_repository() -> InMemoryRepository:
    repository = InMemoryRepository()
    for template in BUILTIN_AGENT_TEMPLATES.values():
        repository.upsert_agent(template)
    return repository


def make_runtime(repository: InMemoryRepository | None = None) -> RuntimeService:
    if repository is None:
        repository = make_repository()
    return RuntimeService(
        repository,
        llm_client=MockLLMClient(),
        web_search=MockWebSearchProvider(),
        vector_store=NoopVectorStore(),
    )


def test_app_can_be_created_with_builtin_agents() -> None:
    repository = make_repository()
    app = create_app(repository)
    assert app.title == "Agent Factory"

    agent_ids = {item.agent_id for item in repository.list_agents()}
    assert "research_agent_default" in agent_ids


def test_research_scan_runtime_slice() -> None:
    repository = make_repository()
    runtime = make_runtime(repository)
    repository.create_task(
        TaskSpec(
            task_id="task_runtime_001",
            title="Search ECG audit papers",
            type="research_scan",
            owner_agent="research_agent_default",
            project_id="ecg_audit",
            priority="high",
            input={
                "topics": ["ECG audit", "medical AI safety"],
                "sources": ["mock_web"],
            },
            expected_output=["paper_candidates", "relevance_scores"],
        )
    )

    run = runtime.run_task("task_runtime_001")
    assert run.status == "completed"
    assert run.output["candidate_memory_id"].startswith("mem_")

    task = repository.get_task("task_runtime_001")
    assert task.status == "completed"

    tool_calls = repository.list_tool_calls()
    assert len(tool_calls) >= 2

    memory_items = repository.list_memory_items()
    candidates = [
        item for item in memory_items if item.source_task_id == "task_runtime_001"
    ]
    assert len(candidates) == 1
    assert candidates[0].status == "candidate"


def test_completed_task_cannot_be_rerun() -> None:
    repository = make_repository()
    runtime = make_runtime(repository)
    repository.create_task(
        TaskSpec(
            task_id="task_runtime_002",
            title="Test completed blocker",
            type="research_scan",
            owner_agent="research_agent_default",
            priority="medium",
            input={"topics": ["test"]},
        )
    )
    runtime.run_task("task_runtime_002")
    task = repository.get_task("task_runtime_002")
    assert task.status == TaskStatus.completed

    try:
        runtime.run_task("task_runtime_002")
        assert False, "should have raised"
    except TaskNotRunnableError:
        pass


def test_failed_task_can_be_retried() -> None:
    repository = make_repository()
    runtime = make_runtime(repository)
    task = TaskSpec(
        task_id="task_runtime_003",
        title="Test retry",
        type="research_scan",
        owner_agent="research_agent_default",
        priority="medium",
        input={"topics": ["test"]},
    )
    task.status = TaskStatus.failed
    repository.create_task(task)

    run = runtime.run_task("task_runtime_003")
    assert run.status == "completed"
    updated = repository.get_task("task_runtime_003")
    assert updated.retry_count == 1
