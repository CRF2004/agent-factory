from __future__ import annotations

from uuid import uuid4

from app.core.clock import utc_now_iso
from app.schemas.approval import ApprovalRequest
from app.schemas.memory import MemoryItem
from app.schemas.run import AgentRun, RunStatus, ToolCall
from app.schemas.task import TaskSpec, TaskStatus, TaskType
from app.services.llm_client import LLMClient
from app.services.repository import Repository
from app.services.vector_store import VectorStore
from app.services.web_search import WebSearchProvider


UNSUPPORTED_STATES_FOR_RUN = {TaskStatus.completed, TaskStatus.running, TaskStatus.cancelled}
RETRYABLE_STATES = {TaskStatus.failed}


class TaskNotRunnableError(ValueError):
    pass


class RuntimeService:
    def __init__(
        self,
        repository: Repository,
        llm_client: LLMClient,
        web_search: WebSearchProvider,
        vector_store: VectorStore,
    ) -> None:
        self.repository = repository
        self.llm = llm_client
        self.search_provider = web_search
        self.vector_store = vector_store

    def run_task(self, task_id: str) -> AgentRun:
        task = self.repository.get_task(task_id)
        self.repository.get_agent(task.owner_agent)

        if task.status in UNSUPPORTED_STATES_FOR_RUN:
            raise TaskNotRunnableError(
                f"task {task_id} is {task.status.value} and cannot be run"
            )
        if task.status == TaskStatus.waiting_approval:
            raise TaskNotRunnableError(
                f"task {task_id} is waiting_approval; resolve approvals before retrying"
            )
        if task.status in RETRYABLE_STATES:
            task.retry_count += 1

        now = utc_now_iso()
        task.status = TaskStatus.running
        self.repository.upsert_task(task)

        run = AgentRun(
            id=f"run_{uuid4().hex}",
            agent_id=task.owner_agent,
            task_id=task.task_id,
            status=RunStatus.running,
            input=task.input,
            started_at=now,
        )
        self.repository.create_run(run)

        try:
            if task.type == TaskType.research_scan:
                run = self._execute_research_scan(task, run)
            else:
                raise ValueError(f"unsupported task type for MVP runtime: {task.type}")
        except Exception as exc:
            run.status = RunStatus.failed
            run.error_message = str(exc)
            run.ended_at = utc_now_iso()
            self.repository.upsert_run(run)

            task.status = TaskStatus.failed
            task.next_action = "investigate_failure"
            self.repository.upsert_task(task)
            raise

        run.status = RunStatus.completed
        run.ended_at = utc_now_iso()
        self.repository.upsert_run(run)

        task.status = TaskStatus.completed
        task.output = run.output
        task.next_action = "review_candidate_memory"
        self.repository.upsert_task(task)

        return run

    def _execute_research_scan(self, task: TaskSpec, run: AgentRun) -> AgentRun:
        topics = task.input.get("topics", [])
        sources = task.input.get("sources", ["web"])
        query = ", ".join(topics) if topics else task.title

        # 1. Web search
        search_results = self.search_provider.search(query, max_results=5)
        search_output = [
            {"title": r.title, "url": r.url, "snippet": r.snippet, "score": r.score}
            for r in search_results
        ]
        search_call = ToolCall(
            id=f"toolcall_{uuid4().hex}",
            run_id=run.id,
            tool_id="web_search",
            input={"query": query, "sources": sources},
            output={"results": search_output},
            status="completed",
            risk_level="low",
        )
        self.repository.create_tool_call(search_call)

        # 2. LLM summarize and score
        snippets_text = "\n\n".join(
            f"[{i+1}] {r.title}\n{r.snippet}\n{r.url}"
            for i, r in enumerate(search_results[:5])
        )
        llm_response = self.llm.chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a research analyst. Summarize the search results below. "
                        "Output JSON with keys: summary (string), relevance_score (float 0-1), "
                        "novelty_score (float 0-1), key_findings (list of strings)."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Query: {query}\n\nSearch results:\n{snippets_text}",
                },
            ],
            temperature=0.3,
            max_tokens=2048,
        )

        llm_content = llm_response.get("content", "{}")
        try:
            import json

            parsed = json.loads(
                llm_content.strip().removeprefix("```json").removesuffix("```").strip()
            )
        except (json.JSONDecodeError, AttributeError):
            parsed = {
                "summary": str(llm_content)[:500],
                "relevance_score": 0.5,
                "novelty_score": 0.5,
                "key_findings": [],
            }

        llm_call = ToolCall(
            id=f"toolcall_{uuid4().hex}",
            run_id=run.id,
            tool_id="llm_call",
            input={"operation": "summarize_and_score", "query": query},
            output={
                "summary": parsed.get("summary", ""),
                "relevance_score": parsed.get("relevance_score", 0.5),
                "novelty_score": parsed.get("novelty_score", 0.5),
                "key_findings": parsed.get("key_findings", []),
            },
            status="completed",
            risk_level="low",
        )
        self.repository.create_tool_call(llm_call)

        # 3. Generate embedding and store in vector DB
        confidence = float(parsed.get("relevance_score", 0.5))
        summary_text = str(parsed.get("summary", ""))
        embedding = None
        try:
            embeddings = self.llm.embed([summary_text])
            embedding = embeddings[0] if embeddings else None
        except Exception:
            embedding = None

        # 4. Create candidate memory
        memory = MemoryItem(
            id=f"mem_{uuid4().hex}",
            type="knowledge",
            title=f"Candidate finding: {query}",
            content=summary_text,
            summary=summary_text,
            source=search_results[0].url if search_results else None,
            source_task_id=task.task_id,
            source_run_id=run.id,
            status="candidate",
            confidence=confidence,
            reliability_score=float(parsed.get("novelty_score", 0.5)),
            tags=list(topics) if isinstance(topics, list) else [],
            related_projects=[task.project_id] if task.project_id else [],
            created_by_agent_id=task.owner_agent,
        )
        self.repository.create_memory_item(memory)

        if embedding:
            try:
                self.vector_store.store(memory.id, embedding)
            except Exception:
                pass

        # auto-create approval for low-confidence memory
        if confidence < 0.6:
            self.repository.create_approval(
                ApprovalRequest(
                    approval_id=f"approval_{uuid4().hex}",
                    requesting_agent=task.owner_agent,
                    task_id=task.task_id,
                    action_type="promote_to_long_term_memory",
                    risk_level="low",
                    summary=f"Low-confidence candidate memory: {memory.title}",
                    details={"confidence": confidence, "memory_id": memory.id},
                    status="pending",
                )
            )

        run.output = {
            "summary": parsed.get("summary", ""),
            "relevance_score": parsed.get("relevance_score", 0.5),
            "novelty_score": parsed.get("novelty_score", 0.5),
            "key_findings": parsed.get("key_findings", []),
            "candidate_memory_id": memory.id,
            "tool_call_ids": [search_call.id, llm_call.id],
        }

        return run
