from __future__ import annotations

from typing import Protocol

from app.schemas.run import AgentRun


class TaskRunner(Protocol):
    def run(self, task_id: str) -> AgentRun: ...
    def run_async(self, task_id: str) -> str: ...


class InProcessTaskRunner:
    def __init__(self, runtime_service) -> None:
        self.runtime = runtime_service

    def run(self, task_id: str) -> AgentRun:
        return self.runtime.run_task(task_id)

    def run_async(self, task_id: str) -> str:
        run = self.runtime.run_task(task_id)
        return run.id
