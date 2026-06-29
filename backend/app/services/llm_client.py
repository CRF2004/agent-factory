from __future__ import annotations

from typing import Any, Protocol

from openai import OpenAI


class LLMClient(Protocol):
    def chat(
        self,
        model: str | None,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]: ...

    def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]: ...


class DmxapiClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://www.dmxapi.cn/v1",
        default_model: str = "gpt-4.1-mini",
        embedding_model: str = "text-embedding-3-small",
    ) -> None:
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.default_model = default_model
        self.embedding_model = embedding_model

    def chat(
        self,
        model: str | None = None,
        messages: list[dict[str, str]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = dict(
            model=model or self.default_model,
            messages=messages or [],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if tools:
            kwargs["tools"] = tools

        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        result: dict[str, Any] = {
            "role": choice.message.role,
            "content": choice.message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            },
        }
        if choice.message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in choice.message.tool_calls
            ]
        return result

    def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=model or self.embedding_model, input=texts
        )
        return [item.embedding for item in response.data]


class MockLLMClient:
    def chat(
        self,
        model: str | None = None,
        messages: list[dict[str, str]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        user_text = ""
        for m in (messages or []):
            if m.get("role") == "user":
                user_text = str(m.get("content", ""))
        return {
            "role": "assistant",
            "content": f"Mock response for: {user_text}",
            "model": "mock-llm",
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
        }

    def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        return [[0.0] * 1536 for _ in texts]
