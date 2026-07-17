from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import sessionmaker

from app.db.init_db import create_schema
from app.db.session import make_engine
from app.schemas.agent_spec import AgentSpec
from app.schemas.heartbeat import AgentHeartbeatState
from app.services.sqlalchemy_repository import SQLAlchemyRepository


def make_repository(database_url: str) -> SQLAlchemyRepository:
    engine = make_engine(database_url)
    create_schema(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    return SQLAlchemyRepository(session_factory)


def test_heartbeat_state_survives_repository_reload(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'heartbeat.db'}"
    repository = make_repository(database_url)
    repository.create_agent(
        AgentSpec(
            agent_id="research-agent",
            name="Research Agent",
            role="researcher",
            mission="Track latest medical AI research",
        )
    )
    state = AgentHeartbeatState(
        agent_id="research-agent",
        last_wakeup_at="2026-07-17T09:00:00+00:00",
        next_wakeup_at="2026-07-17T10:00:00+00:00",
        last_task_id="task-1",
    )
    repository.upsert_heartbeat_state(state)

    reloaded = make_repository(database_url).get_heartbeat_state("research-agent")

    assert reloaded.last_wakeup_at == state.last_wakeup_at
    assert reloaded.next_wakeup_at == state.next_wakeup_at
    assert reloaded.last_task_id == "task-1"


def test_sqlalchemy_heartbeat_lease_blocks_second_holder(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'heartbeat-lease.db'}"
    repository = make_repository(database_url)
    repository.create_agent(
        AgentSpec(
            agent_id="research-agent",
            name="Research Agent",
            role="researcher",
            mission="Track latest medical AI research",
        )
    )
    now = datetime(2026, 7, 17, 9, 0, tzinfo=UTC)

    first = repository.acquire_heartbeat_lease(
        agent_id="research-agent",
        lease_token="first",
        now=now.isoformat(),
        lease_until=(now + timedelta(minutes=5)).isoformat(),
    )
    second = repository.acquire_heartbeat_lease(
        agent_id="research-agent",
        lease_token="second",
        now=now.isoformat(),
        lease_until=(now + timedelta(minutes=5)).isoformat(),
    )

    assert first is not None
    assert second is None
