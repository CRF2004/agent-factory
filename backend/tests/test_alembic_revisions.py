from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_has_single_heartbeat_head() -> None:
    script = ScriptDirectory.from_config(Config("alembic.ini"))

    assert script.get_heads() == ["0003"]
    assert script.get_revision("0003").down_revision == "0002"
    assert script.get_revision("0002").down_revision == "0001_phase0_schema"
