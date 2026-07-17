"""add persistent agent heartbeat states

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-17
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def json_type():
    return postgresql.JSONB().with_variant(sa.JSON(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "agent_heartbeat_states",
        sa.Column(
            "agent_id",
            sa.Text(),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("next_wakeup_at", sa.Text()),
        sa.Column("lease_token", sa.Text()),
        sa.Column("lease_until", sa.Text()),
        sa.Column("state_json", json_type(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "idx_agent_heartbeat_states_next_wakeup_at",
        "agent_heartbeat_states",
        ["next_wakeup_at"],
    )
    op.create_index(
        "idx_agent_heartbeat_states_lease_until",
        "agent_heartbeat_states",
        ["lease_until"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_agent_heartbeat_states_lease_until",
        table_name="agent_heartbeat_states",
    )
    op.drop_index(
        "idx_agent_heartbeat_states_next_wakeup_at",
        table_name="agent_heartbeat_states",
    )
    op.drop_table("agent_heartbeat_states")
