from __future__ import annotations

from app.schemas.agent_spec import AgentSpec


BUILTIN_AGENT_TEMPLATES: dict[str, AgentSpec] = {
    "research_agent": AgentSpec(
        agent_id="research_agent_default",
        name="Research Agent",
        role="Research Agent",
        mission="Monitor configured sources, identify relevant information, summarize findings, and create candidate memories or tasks.",
        status="idle",
        autonomy_level="L2",
        project_ids=[],
        triggers=[
            {
                "type": "schedule",
                "cron": "0 8 * * *",
                "enabled": True,
                "input": {"task_type": "research_scan"},
            }
        ],
        tools=[
            {"tool_id": "web_search", "permission": "read_only"},
            {"tool_id": "browser_fetch", "permission": "read_only"},
            {"tool_id": "llm_call", "permission": "read_only"},
            {"tool_id": "vector_db", "permission": "write_memory"},
            {"tool_id": "postgres_task_db", "permission": "write_memory"},
        ],
        memory_access={
            "read": ["knowledge_base", "experience_base", "project_context"],
            "write": ["candidate_memory"],
            "require_source": True,
            "low_confidence_requires_review": True,
        },
        actions={
            "auto": [
                "search_sources",
                "summarize",
                "score_relevance",
                "create_candidate_memory",
            ],
            "approval_required": ["write_long_term_memory", "send_external_message"],
        },
        evaluation=[
            "source_required",
            "relevance_score_required",
            "duplication_check",
        ],
    ),
    "project_manager_agent": AgentSpec(
        agent_id="project_manager_agent_default",
        name="Project Manager Agent",
        role="Project Manager Agent",
        mission="Review project state, identify blocked or overdue work, and propose concrete next actions.",
        status="idle",
        autonomy_level="L2",
        tools=[
            {"tool_id": "postgres_task_db", "permission": "write_memory"},
            {"tool_id": "local_file_read", "permission": "read_only"},
            {"tool_id": "llm_call", "permission": "read_only"},
        ],
        memory_access={
            "read": ["project_context", "experience_base", "knowledge_base"],
            "write": ["candidate_memory"],
            "require_source": True,
            "low_confidence_requires_review": True,
        },
        actions={
            "auto": ["review_tasks", "mark_blockers", "create_candidate_tasks"],
            "approval_required": ["send_email", "create_calendar_event"],
        },
        evaluation=["audit_log_required"],
    ),
    "memory_curator_agent": AgentSpec(
        agent_id="memory_curator_agent_default",
        name="Memory Curator Agent",
        role="Memory Curator Agent",
        mission="Review candidate memories, classify them, detect conflicts, and promote reliable items into long-term memory.",
        status="idle",
        autonomy_level="L2",
        tools=[
            {"tool_id": "vector_db", "permission": "write_memory"},
            {"tool_id": "postgres_task_db", "permission": "write_memory"},
            {"tool_id": "llm_call", "permission": "read_only"},
        ],
        memory_access={
            "read": ["candidate_memory", "knowledge_base", "experience_base", "skill_store"],
            "write": ["knowledge_base", "experience_base", "skill_store"],
            "require_source": True,
            "low_confidence_requires_review": True,
        },
        actions={
            "auto": ["classify_memory", "detect_duplicates", "mark_conflicts"],
            "approval_required": ["promote_low_confidence_memory", "modify_skill"],
        },
        evaluation=["source_required", "confidence_required", "duplication_check"],
    ),
}
