import os
import sys
from sqlalchemy import select

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.app import models


def test_save_data_to_database(db_session):
    user = models.User(
        email="example@test.py",
        password_hash="argon2-hashedpass",
    )

    db_session.add(user)
    db_session.commit()

    db_session.expire_all()

    statement = select(models.User)
    users = db_session.scalars(statement).all()

    assert len(users) == 1
    assert user.user_id is not None
    assert user.email == "example@test.py"


def test_rollback_option(db_session):
    user = models.User(
        email="example@test.py",
        password_hash="argon2-hashedpass",
    )

    db_session.add(user)
    db_session.flush()

    assert user.user_id is not None

    db_session.rollback()

    statement = select(models.User)
    users = db_session.scalars(statement).all()

    assert users == []
