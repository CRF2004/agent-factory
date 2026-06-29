from __future__ import annotations

from fastapi import FastAPI

from app.api.deps import get_repository, get_runtime_service
from app.api.routes import router
from app.services.llm_client import MockLLMClient
from app.services.repository import Repository
from app.services.runtime import RuntimeService
from app.services.vector_store import NoopVectorStore
from app.services.web_search import MockWebSearchProvider


def create_app(repository: Repository | None = None) -> FastAPI:
    app = FastAPI(
        title="Agent Factory",
        version="0.1.0",
        description="Workspace for defining, running, and operating long-lived personal agents.",
    )

    if repository is not None:
        runtime = RuntimeService(
            repository,
            llm_client=MockLLMClient(),
            web_search=MockWebSearchProvider(),
            vector_store=NoopVectorStore(),
        )
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_runtime_service] = lambda: runtime

    app.include_router(router, prefix="/api")
    return app


app = create_app()
