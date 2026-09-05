import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.app.service import (
    create_user,
    login_user,
)
from src.app.schemas import (
    UserCreate,
    UserLogin,
)
from src.app.exceptions import InvalidCredentialsError


def create_user_for_tests(db_session, email, password):
    user_data = UserCreate(
        email=email,
        password=password,
    )

    user = create_user(db_session, user_data)

    return user


def test_create_account(db_session):
    response = create_user_for_tests(db_session, "example@test.py", "qwerty")

    assert response.email == "example@test.py"
    assert response.password_hash != "qwerty"
    assert response.role == "user"


def test_login_user(db_session):
    create_user_for_tests(db_session, "example@test.py", "qwerty")

    user_login_data = UserLogin(
        email="example@test.py",
        password="qwerty",
    )
    response = login_user(db_session, user_login_data)

    assert response.access_token is not None
    assert response.token_type == "bearer"


def test_login_user_with_wrong_password(db_session):
    create_user_for_tests(db_session, "example@test.py", "qwerty")

    user_login_data = UserLogin(
        email="example@test.py",
        password="ytrewq",
    )

    with pytest.raises(InvalidCredentialsError):
        login_user(db_session, user_login_data)


def test_users_with_identical_passwords(db_session):
    response_create_first = create_user_for_tests(db_session, "example_1@test.py", "qwerty")
    response_create_second = create_user_for_tests(db_session, "example_2@test.py", "qwerty")

    password_hash_first = response_create_first.password_hash
    password_hash_second = response_create_second.password_hash

    assert password_hash_first != password_hash_second
