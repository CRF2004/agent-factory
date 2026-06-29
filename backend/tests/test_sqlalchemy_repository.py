from sqlalchemy.orm import sessionmaker

from app.db.init_db import create_schema
from app.db.session import make_engine
from app.schemas.task import TaskSpec
from app.services.llm_client import MockLLMClient
from app.services.runtime import RuntimeService
from app.services.sqlalchemy_repository import SQLAlchemyRepository
from app.services.vector_store import NoopVectorStore
from app.services.web_search import MockWebSearchProvider
from app.templates.builtin_agents import BUILTIN_AGENT_TEMPLATES


def make_persistent_repository(database_url: str) -> SQLAlchemyRepository:
    engine = make_engine(database_url)
    create_schema(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    return SQLAlchemyRepository(session_factory)


def test_sqlalchemy_repository_persists_runtime_state(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent_factory.db'}"
    repository = make_persistent_repository(database_url)
    for template in BUILTIN_AGENT_TEMPLATES.values():
        repository.upsert_agent(template)

    repository.create_task(
        TaskSpec(
            task_id="task_persist_001",
            title="Search persistent ECG audit papers",
            type="research_scan",
            owner_agent="research_agent_default",
            project_id="ecg_audit",
            priority="high",
            input={
                "topics": ["ECG audit"],
                "sources": ["mock_web"],
            },
            expected_output=["paper_candidates", "relevance_scores"],
        )
    )

    runtime = RuntimeService(
        repository,
        llm_client=MockLLMClient(),
        web_search=MockWebSearchProvider(),
        vector_store=NoopVectorStore(),
    )
    run = runtime.run_task("task_persist_001")
    assert run.status == "completed"

    reloaded_repository = make_persistent_repository(database_url)
    task = reloaded_repository.get_task("task_persist_001")
    assert task.status == "completed"
    assert task.output["candidate_memory_id"].startswith("mem_")
    assert len(reloaded_repository.list_runs()) == 1
    assert len(reloaded_repository.list_tool_calls()) == 2
    assert len(reloaded_repository.list_memory_items()) == 1
