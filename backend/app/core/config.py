from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    database_url: str | None = None
    repository_backend: str = "memory"

    # dmxapi (OpenAI-compatible LLM provider)
    dmxapi_api_key: str = ""
    dmxapi_base_url: str = "https://www.dmxapi.cn/v1"
    dmxapi_default_model: str = "deepseek-v4-flash-guan"
    dmxapi_embedding_model: str = "text-embedding-3-small"

    # tavily web search
    tavily_api_key: str = ""

    # pgvector
    vector_enabled: bool = True
    vector_dimension: int = 1536


def get_settings() -> Settings:
    database_url = os.getenv("AGENT_FACTORY_DATABASE_URL")
    return Settings(
        database_url=database_url,
        repository_backend=os.getenv(
            "AGENT_FACTORY_REPOSITORY_BACKEND",
            "postgres" if database_url else "memory",
        ),
        dmxapi_api_key=os.getenv("DMXAPI_API_KEY", ""),
        dmxapi_base_url=os.getenv("DMXAPI_BASE_URL", "https://www.dmxapi.cn/v1"),
        dmxapi_default_model=os.getenv("DMXAPI_DEFAULT_MODEL", "deepseek-v4-flash-guan"),
        dmxapi_embedding_model=os.getenv("DMXAPI_EMBEDDING_MODEL", "text-embedding-3-small"),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        vector_enabled=os.getenv("VECTOR_ENABLED", "1") not in ("0", "false", "False"),
        vector_dimension=int(os.getenv("VECTOR_DIMENSION", "1536")),
    )
