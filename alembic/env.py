from logging.config import fileConfig
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, pool
from alembic import context

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from src.app.database import Base
from src.app import models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

arguments = context.get_x_argument(as_dictionary=True)

db_mode = "db"
if arguments.get(db_mode) == "test":
    environment_key = "DATABASE_TEST_URL"
elif arguments.get(db_mode) == "migration":
    environment_key = "DATABASE_MIGRATION_TEST_URL"
else:
    environment_key = "DATABASE_URL"

database_url = os.getenv(environment_key)
if not database_url:
    raise RuntimeError(f"{environment_key} no found in .env")

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(
        database_url,
        poolclass=pool.NullPool
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
