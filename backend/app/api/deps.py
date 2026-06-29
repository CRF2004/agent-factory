from __future__ import annotations

from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.db.session import make_session_factory
from app.services.llm_client import DmxapiClient, MockLLMClient
from app.services.repository import InMemoryRepository
from app.services.runtime import RuntimeService
from app.services.sqlalchemy_repository import SQLAlchemyRepository
from app.services.vector_store import NoopVectorStore, PgvectorVectorStore
from app.services.web_search import MockWebSearchProvider, TavilySearchProvider
from app.templates.builtin_agents import BUILTIN_AGENT_TEMPLATES


def seed_builtin_agents(repository) -> None:
    for template in BUILTIN_AGENT_TEMPLATES.values():
        repository.upsert_agent(template)


settings = get_settings()
session_factory: sessionmaker | None = None

if settings.repository_backend == "postgres":
    if not settings.database_url:
        raise RuntimeError("AGENT_FACTORY_DATABASE_URL is required for postgres backend")
    session_factory = make_session_factory(settings.database_url)
    repository = SQLAlchemyRepository(session_factory)
else:
    repository = InMemoryRepository()

seed_builtin_agents(repository)

if settings.dmxapi_api_key:
    llm_client = DmxapiClient(
        api_key=settings.dmxapi_api_key,
        base_url=settings.dmxapi_base_url,
        default_model=settings.dmxapi_default_model,
        embedding_model=settings.dmxapi_embedding_model,
    )
else:
    llm_client = MockLLMClient()

if settings.tavily_api_key:
    web_search = TavilySearchProvider(api_key=settings.tavily_api_key)
else:
    web_search = MockWebSearchProvider()

if settings.vector_enabled and session_factory is not None:
    vector_store = PgvectorVectorStore(session_factory, dimension=settings.vector_dimension)
else:
    vector_store = NoopVectorStore()

runtime_service = RuntimeService(repository, llm_client, web_search, vector_store)


def get_repository():
    return repository


def get_runtime_service() -> RuntimeService:
    return runtime_service


def get_llm_client():
    return llm_client


def get_web_search_provider():
    return web_search


def get_vector_store():
    return vector_store
