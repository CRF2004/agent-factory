"""phase0 schema

Revision ID: 0001_phase0_schema
Revises:
Create Date: 2026-06-29
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_phase0_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def json_type():
    return postgresql.JSONB().with_variant(sa.JSON(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("mission", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("autonomy_level", sa.Text(), nullable=False),
        sa.Column("spec_json", json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("project_id", sa.Text()),
        sa.Column("owner_agent_id", sa.Text(), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("priority", sa.Text(), nullable=False),
        sa.Column("input_json", json_type(), nullable=False),
        sa.Column("output_json", json_type(), nullable=False),
        sa.Column("created_by", sa.Text(), nullable=False),
        sa.Column("spec_json", json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_tasks_owner_agent_id", "tasks", ["owner_agent_id"])
    op.create_index("idx_tasks_status", "tasks", ["status"])
    op.create_index("idx_tasks_project_id", "tasks", ["project_id"])

    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("agent_id", sa.Text(), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("task_id", sa.Text(), sa.ForeignKey("tasks.id"), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("input_json", json_type(), nullable=False),
        sa.Column("output_json", json_type(), nullable=False),
        sa.Column("started_at", sa.Text(), nullable=False),
        sa.Column("ended_at", sa.Text()),
        sa.Column("error_message", sa.Text()),
        sa.Column("cost", sa.Numeric()),
        sa.Column("spec_json", json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_agent_runs_agent_id", "agent_runs", ["agent_id"])
    op.create_index("idx_agent_runs_task_id", "agent_runs", ["task_id"])
    op.create_index("idx_agent_runs_status", "agent_runs", ["status"])

    op.create_table(
        "tool_calls",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("run_id", sa.Text(), sa.ForeignKey("agent_runs.id"), nullable=False),
        sa.Column("tool_id", sa.Text(), nullable=False),
        sa.Column("input_json", json_type(), nullable=False),
        sa.Column("output_json", json_type(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("risk_level", sa.Text(), nullable=False),
        sa.Column("spec_json", json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_tool_calls_run_id", "tool_calls", ["run_id"])
    op.create_index("idx_tool_calls_tool_id", "tool_calls", ["tool_id"])

    op.create_table(
        "memory_items",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("source_task_id", sa.Text(), sa.ForeignKey("tasks.id")),
        sa.Column("source_run_id", sa.Text(), sa.ForeignKey("agent_runs.id")),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Numeric(), nullable=False),
        sa.Column("spec_json", json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_memory_items_type", "memory_items", ["type"])
    op.create_index("idx_memory_items_status", "memory_items", ["status"])
    op.create_index("idx_memory_items_source_task_id", "memory_items", ["source_task_id"])

    op.create_table(
        "approvals",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("requesting_agent_id", sa.Text(), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("task_id", sa.Text(), sa.ForeignKey("tasks.id")),
        sa.Column("action_type", sa.Text(), nullable=False),
        sa.Column("risk_level", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("details_json", json_type(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("spec_json", json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_approvals_status", "approvals", ["status"])
    op.create_index("idx_approvals_requesting_agent_id", "approvals", ["requesting_agent_id"])

    op.create_table(
        "schedules",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("agent_id", sa.Text(), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("task_type", sa.Text(), nullable=False),
        sa.Column("cron", sa.Text(), nullable=False),
        sa.Column("input_json", json_type(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("last_run_at", sa.Text()),
        sa.Column("next_run_at", sa.Text()),
        sa.Column("spec_json", json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_schedules_agent_id", "schedules", ["agent_id"])
    op.create_index("idx_schedules_enabled", "schedules", ["enabled"])


def downgrade() -> None:
    op.drop_index("idx_schedules_enabled", table_name="schedules")
    op.drop_index("idx_schedules_agent_id", table_name="schedules")
    op.drop_table("schedules")
    op.drop_index("idx_approvals_requesting_agent_id", table_name="approvals")
    op.drop_index("idx_approvals_status", table_name="approvals")
    op.drop_table("approvals")
    op.drop_index("idx_memory_items_source_task_id", table_name="memory_items")
    op.drop_index("idx_memory_items_status", table_name="memory_items")
    op.drop_index("idx_memory_items_type", table_name="memory_items")
    op.drop_table("memory_items")
    op.drop_index("idx_tool_calls_tool_id", table_name="tool_calls")
    op.drop_index("idx_tool_calls_run_id", table_name="tool_calls")
    op.drop_table("tool_calls")
    op.drop_index("idx_agent_runs_status", table_name="agent_runs")
    op.drop_index("idx_agent_runs_task_id", table_name="agent_runs")
    op.drop_index("idx_agent_runs_agent_id", table_name="agent_runs")
    op.drop_table("agent_runs")
    op.drop_index("idx_tasks_project_id", table_name="tasks")
    op.drop_index("idx_tasks_status", table_name="tasks")
    op.drop_index("idx_tasks_owner_agent_id", table_name="tasks")
    op.drop_table("tasks")
    op.drop_table("agents")
