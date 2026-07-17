from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app
from app.schemas.agent_spec import AgentSpec
from app.services.repository import InMemoryRepository


def test_heartbeat_api_executes_and_reports_state(monkeypatch) -> None:
    monkeypatch.setenv("AGENT_FACTORY_HEARTBEAT_ENABLED", "0")
    repository = InMemoryRepository()
    repository.create_agent(
        AgentSpec(
            agent_id="research-agent",
            name="Research Agent",
            role="researcher",
            mission="Track latest medical AI research",
        )
    )
    client = TestClient(create_app(repository))

    first = client.post("/api/agents/research-agent/heartbeat")
    second = client.post("/api/agents/research-agent/heartbeat")
    state = client.get("/api/agents/research-agent/heartbeat")

    assert first.status_code == 200
    assert first.json()["action"] == "task_created"
    assert first.json()["task"]["status"] == "completed"
    assert first.json()["experience_memory"]["type"] == "experience"
    assert second.status_code == 200
    assert second.json()["action"] == "no_action"
    assert state.status_code == 200
    assert state.json()["last_task_id"] == first.json()["task"]["task_id"]


def test_run_due_heartbeats_api(monkeypatch) -> None:
    monkeypatch.setenv("AGENT_FACTORY_HEARTBEAT_ENABLED", "0")
    repository = InMemoryRepository()
    repository.create_agent(
        AgentSpec(
            agent_id="research-agent",
            name="Research Agent",
            role="researcher",
            mission="Track latest medical AI research",
        )
    )
    client = TestClient(create_app(repository))

    response = client.post("/api/agents/heartbeat/run-due")

    assert response.status_code == 200
    assert response.json()["checked_agents"] == 1
    assert response.json()["due_agents"] == 1
    assert response.json()["results"][0]["action"] == "task_created"
