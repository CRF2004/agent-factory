from __future__ import annotations

from typing import Protocol


class VectorStore(Protocol):
    def store(self, memory_id: str, embedding: list[float]) -> None: ...
    def search(self, embedding: list[float], k: int = 5) -> list[tuple[str, float]]: ...
    def delete(self, memory_id: str) -> None: ...


class PgvectorVectorStore:
    def __init__(self, session_factory, dimension: int = 1536) -> None:
        self.session_factory = session_factory
        self.dimension = dimension

    def store(self, memory_id: str, embedding: list[float]) -> None:
        from sqlalchemy import text

        with self.session_factory() as session:
            session.execute(
                text(
                    "UPDATE memory_items SET embedding = :embedding WHERE id = :id"
                ),
                {"embedding": embedding, "id": memory_id},
            )
            session.commit()

    def search(self, embedding: list[float], k: int = 5) -> list[tuple[str, float]]:
        from sqlalchemy import text

        with self.session_factory() as session:
            rows = session.execute(
                text(
                    "SELECT id, 1 - (embedding <=> :embedding) AS similarity "
                    "FROM memory_items "
                    "WHERE embedding IS NOT NULL "
                    "ORDER BY embedding <=> :embedding "
                    "LIMIT :k"
                ),
                {"embedding": embedding, "k": k},
            ).fetchall()
            return [(row[0], float(row[1])) for row in rows]

    def delete(self, memory_id: str) -> None:
        from sqlalchemy import text

        with self.session_factory() as session:
            session.execute(
                text(
                    "UPDATE memory_items SET embedding = NULL WHERE id = :id"
                ),
                {"id": memory_id},
            )
            session.commit()


class NoopVectorStore:
    def store(self, memory_id: str, embedding: list[float]) -> None:
        pass

    def search(self, embedding: list[float], k: int = 5) -> list[tuple[str, float]]:
        return []

    def delete(self, memory_id: str) -> None:
        pass
