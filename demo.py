from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from app.agent_runtime.runtime import AutonomousRuntime
from app.schemas.agent_spec import AgentSpec
from app.services.llm_client import MockLLMClient
from app.services.repository import InMemoryRepository
from app.services.runtime import RuntimeService
from app.services.vector_store import NoopVectorStore
from app.services.web_search import MockWebSearchProvider


def main() -> None:
    repository = InMemoryRepository()
    agent = AgentSpec(
        agent_id="research-agent",
        name="Research Agent",
        role="researcher",
        mission="Track latest medical AI research",
    )
    repository.create_agent(agent)

    runtime = RuntimeService(
        repository=repository,
        llm_client=MockLLMClient(),
        web_search=MockWebSearchProvider(),
        vector_store=NoopVectorStore(),
    )
    autonomous_runtime = AutonomousRuntime(repository, runtime)

    print("Research Agent started\n")
    print("Heartbeat triggered\n")

    result = autonomous_runtime.run_once(agent.agent_id)

    print("Observation:")
    print(
        "No active research task"
        if not result.observation.get("active_tasks")
        else "Active task detected"
    )
    print("\nPlanner decision:")
    print(
        f"Create {result.planned_tasks[0].type.value} task"
        if result.planned_tasks
        else "No action"
    )

    if result.executed_task:
        print("\nTask created:")
        print(f'"{result.executed_task.title}"')

    if result.run:
        print("\nRuntime executed:")
        print(f"Run status: {result.run.status.value}")

    if result.experience_memory:
        print("\nReflection:")
        print(
            "Created experience memory "
            f"{result.experience_memory.id} ({result.experience_memory.status.value})"
        )

    print("\nAgent sleeping...")


if __name__ == "__main__":
    main()
