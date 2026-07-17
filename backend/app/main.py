from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agent_runtime.lifecycle.heartbeat import HeartbeatService
from app.agent_runtime.lifecycle.runner import HeartbeatRunner
from app.agent_runtime.runtime import AutonomousRuntime
from app.api.deps import (
    get_heartbeat_service,
    get_repository,
    get_runtime_service,
)
from app.api.deps import heartbeat_service as default_heartbeat_service
from app.api.routes import router
from app.core.config import get_settings
from app.services.llm_client import MockLLMClient
from app.services.repository import Repository
from app.services.runtime import RuntimeService
from app.services.vector_store import NoopVectorStore
from app.services.web_search import MockWebSearchProvider


def create_app(repository: Repository | None = None) -> FastAPI:
    settings = get_settings()
    local_runtime: RuntimeService | None = None
    service = default_heartbeat_service

    if repository is not None:
        local_runtime = RuntimeService(
            repository,
            llm_client=MockLLMClient(),
            web_search=MockWebSearchProvider(),
            vector_store=NoopVectorStore(),
        )
        service = HeartbeatService(
            repository=repository,
            autonomous_runtime=AutonomousRuntime(repository, local_runtime),
            default_wakeup_seconds=settings.default_wakeup_seconds,
            lease_seconds=settings.heartbeat_lease_seconds,
        )

    runner = (
        HeartbeatRunner(service, poll_seconds=settings.heartbeat_poll_seconds)
        if settings.heartbeat_enabled
        else None
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if runner is not None:
            runner.start()
        try:
            yield
        finally:
            if runner is not None:
                runner.stop()

    app = FastAPI(
        title="Agent Factory",
        version="0.2.0",
        description="Workspace for defining, running, and operating long-lived personal agents.",
        lifespan=lifespan,
    )

    if repository is not None and local_runtime is not None:
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_runtime_service] = lambda: local_runtime
        app.dependency_overrides[get_heartbeat_service] = lambda: service

    app.state.heartbeat_service = service
    app.state.heartbeat_runner = runner
    app.include_router(router, prefix="/api")
    return app


app = create_app()
