"""add pgvector embedding column to memory_items

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-29
"""
from collections.abc import Sequence

from alembic import op
from sqlalchemy import Text

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(
        "ALTER TABLE memory_items ADD COLUMN IF NOT EXISTS embedding vector(1536)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE memory_items DROP COLUMN IF EXISTS embedding")
