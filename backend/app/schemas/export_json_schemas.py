from __future__ import annotations

import json
from pathlib import Path

from app.schemas.agent_spec import AgentSpec
from app.schemas.approval import ApprovalRequest
from app.schemas.memory import MemoryItem, SkillSpec
from app.schemas.run import AgentRun, ToolCall
from app.schemas.schedule import ScheduleSpec
from app.schemas.task import TaskSpec
from app.schemas.tool import ToolSpec


def export_json_schemas(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    models = {
        "agent_spec.schema.json": AgentSpec,
        "task.schema.json": TaskSpec,
        "tool.schema.json": ToolSpec,
        "memory.schema.json": MemoryItem,
        "skill.schema.json": SkillSpec,
        "agent_run.schema.json": AgentRun,
        "tool_call.schema.json": ToolCall,
        "approval.schema.json": ApprovalRequest,
        "schedule.schema.json": ScheduleSpec,
    }
    for filename, model in models.items():
        payload = json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False)
        (output_dir / filename).write_text(payload + "\n", encoding="utf-8")


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[3]
    export_json_schemas(repo_root / "specs")
