import os
import sys
import pytest
from sqlalchemy.exc import IntegrityError

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.app import models


# =========================================================
#                        HAPPY PATH
# =========================================================
def test_create_user_in_database(db_session):
    user = models.User(
        email="example@test.py",
        password_hash="argon2-hashedpass",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert isinstance(user.user_id, int)
    assert user.email == "example@test.py"


# =========================================================
#                         SAD PATH
# =========================================================
def test_create_existing_user_in_database(db_session):
    user_first = models.User(
        email="example@test.py",
        password_hash="argon2-hashedpass",
    )

    db_session.add(user_first)
    db_session.commit()
    db_session.refresh(user_first)

    user_second = models.User(
        email="example@test.py",
        password_hash="argon2-hashedpass",
    )

    with pytest.raises(IntegrityError):
        db_session.add(user_second)
        db_session.commit()


def test_create_user_with_incorrectly_role_in_database(db_session):
    user = models.User(
        email="example@test.py",
        password_hash="argon2-hashedpass",
        role="not-allowed-role",
    )

    with pytest.raises(IntegrityError):
        db_session.add(user)
        db_session.commit()
