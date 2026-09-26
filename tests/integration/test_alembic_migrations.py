from argparse import Namespace

from alembic.config import Config
from sqlalchemy import inspect

from alembic import command


def test_alembic_upgrade_head_command(migration_engine):
    alembic_config = Config(
        "alembic.ini",
        cmd_opts=Namespace(x=["db=migration"]),
    )

    command.downgrade(alembic_config, "base")

    try:
        command.upgrade(alembic_config, "head")

        inspector = inspect(migration_engine)

        tables = inspector.get_table_names()

        assert "alembic_version" in tables
        assert "users" in tables
        assert "rooms" in tables
        assert "bookings" in tables

    finally:
        command.downgrade(alembic_config, "base")