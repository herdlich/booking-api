import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from pathlib import Path

from src.app import models
from src.app.api import app
from src.app.database import get_session

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


@pytest.fixture(scope="session")
def test_engine():
    database_test_url = os.getenv("DATABASE_TEST_URL")

    if not database_test_url:
        raise Exception("DATABASE_TEST_URL not set")

    engine = create_engine(database_test_url)

    models.Base.metadata.create_all(bind=engine)

    yield engine

    engine.dispose()


@pytest.fixture(scope="session")
def migration_engine():
    database_migration_test_url = os.getenv("DATABASE_MIGRATION_TEST_URL")

    if not database_migration_test_url:
        raise Exception("DATABASE_MIGRATION_TEST_URL not set")

    engine = create_engine(database_migration_test_url)

    yield engine

    engine.dispose()


@pytest.fixture()
def db_session(test_engine):
    SessionFactory = sessionmaker(bind=test_engine)
    session = SessionFactory()

    try:
        yield session
    finally:
        session.rollback()

        session.execute(delete(models.Booking))
        session.execute(delete(models.Room))
        session.execute(delete(models.User))

        session.commit()

        session.close()


@pytest.fixture()
def client(db_session):
    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()
