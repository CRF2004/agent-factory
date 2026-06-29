from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    raw_content: str | None = None
    score: float | None = None


class WebSearchProvider(Protocol):
    def search(
        self,
        query: str,
        max_results: int = 5,
        include_raw_content: bool = False,
    ) -> list[SearchResult]: ...


class TavilySearchProvider:
    def __init__(self, api_key: str) -> None:
        from tavily import TavilyClient

        self.client = TavilyClient(api_key=api_key)

    def search(
        self,
        query: str,
        max_results: int = 5,
        include_raw_content: bool = False,
    ) -> list[SearchResult]:
        response = self.client.search(
            query=query,
            max_results=max_results,
            include_raw_content=include_raw_content,
        )
        results: list[SearchResult] = []
        for item in response.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", ""),
                    raw_content=item.get("raw_content"),
                    score=item.get("score"),
                )
            )
        return results


class MockWebSearchProvider:
    def search(
        self,
        query: str,
        max_results: int = 5,
        include_raw_content: bool = False,
    ) -> list[SearchResult]:
        return [
            SearchResult(
                title=f"Mock result for: {query}",
                url="https://example.com/mock-result",
                snippet=f"A simulated search finding about {query}. This is mock data for development.",
                score=0.85,
            )
            for _ in range(min(max_results, 3))
        ]
