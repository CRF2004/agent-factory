from __future__ import annotations

from uuid import uuid4

from app.schemas.agent_spec import AgentSpec
from app.schemas.memory import MemoryItem, MemoryStatus, MemoryType
from app.schemas.run import AgentRun
from app.schemas.task import TaskSpec
from app.services.repository import Repository


class ReflectionEngine:
    """Convert a completed run into reusable experience memory."""

    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def reflect(
        self,
        agent: AgentSpec,
        task: TaskSpec,
        run: AgentRun,
    ) -> MemoryItem:
        tool_calls = [
            call for call in self.repository.list_tool_calls() if call.run_id == run.id
        ]
        tool_ids = [call.tool_id for call in tool_calls]
        summary = str(run.output.get("summary") or "Task completed without a summary.")
        findings = run.output.get("key_findings", [])
        if not isinstance(findings, list):
            findings = [str(findings)]

        topics = task.input.get("topics", [])
        if not isinstance(topics, list):
            topics = [str(topics)]

        content_lines = [
            f"Task type: {task.type.value}",
            f"Mission: {agent.mission}",
            f"Outcome: {summary}",
            f"Effective approach: topics={topics or [task.title]}; tools={tool_ids or ['none']}",
        ]
        if findings:
            content_lines.append(
                "Reusable findings: " + "; ".join(str(item) for item in findings[:5])
            )
        content_lines.append(
            "Next use: reuse the same focused query structure before broadening scope."
        )

        confidence = self._confidence(run)
        memory = MemoryItem(
            id=f"mem_{uuid4().hex}",
            type=MemoryType.experience,
            title=f"Experience: {task.title}",
            content="\n".join(content_lines),
            summary=summary[:500],
            source_task_id=task.task_id,
            source_run_id=run.id,
            status=MemoryStatus.candidate,
            confidence=confidence,
            reliability_score=confidence,
            tags=["autonomous-reflection", task.type.value, *[str(t) for t in topics[:3]]],
            related_projects=[task.project_id] if task.project_id else [],
            created_by_agent_id=agent.agent_id,
        )
        return self.repository.create_memory_item(memory)

    @staticmethod
    def _confidence(run: AgentRun) -> float:
        raw = run.output.get("relevance_score", 0.7)
        try:
            return max(0.0, min(1.0, float(raw)))
        except (TypeError, ValueError):
            return 0.7
