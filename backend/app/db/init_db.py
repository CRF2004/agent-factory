from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import tables  # noqa: F401
from app.templates.builtin_agents import BUILTIN_AGENT_TEMPLATES


def create_schema(engine) -> None:
    Base.metadata.create_all(bind=engine)


def seed_builtin_agents(session: Session) -> None:
    from app.models.tables import AgentRecord

    for template in BUILTIN_AGENT_TEMPLATES.values():
        payload = template.model_dump(mode="json")
        session.merge(
            AgentRecord(
                id=template.agent_id,
                name=template.name,
                role=template.role,
                mission=template.mission,
                status=template.status.value,
                autonomy_level=template.autonomy_level.value,
                spec_json=payload,
            )
        )
    session.commit()
