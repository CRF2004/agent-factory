import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.schemas.agent_spec import AgentSpec
from app.schemas.approval import ApprovalRequest
from app.schemas.memory import MemoryItem
from app.schemas.schedule import ScheduleSpec
from app.schemas.task import TaskSpec
from app.schemas.tool import ToolSpec
from app.templates.builtin_agents import BUILTIN_AGENT_TEMPLATES


def test_builtin_templates_are_valid() -> None:
    assert {"research_agent", "project_manager_agent", "memory_curator_agent"} <= set(
        BUILTIN_AGENT_TEMPLATES
    )
    for template in BUILTIN_AGENT_TEMPLATES.values():
        assert isinstance(template, AgentSpec)
        assert template.agent_id


def test_phase0_core_models_validate() -> None:
    ToolSpec(
        tool_id="web_search",
        name="Web Search",
        type="information",
        permission="read_only",
    )
    TaskSpec(
        task_id="task_001",
        title="Search new papers",
        type="research_scan",
        owner_agent="research_agent_default",
    )
    MemoryItem(
        id="mem_001",
        type="knowledge",
        title="Paper candidate",
        content="A sourced summary.",
        confidence=0.8,
    )
    ApprovalRequest(
        approval_id="approval_001",
        requesting_agent="research_agent_default",
        action_type="write_external",
        risk_level="high",
        summary="Draft external action requires approval.",
    )
    ScheduleSpec(
        schedule_id="daily_research_scan",
        agent_id="research_agent_default",
        task_type="research_scan",
        cron="0 8 * * *",
    )
