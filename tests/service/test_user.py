import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.app.exceptions import InvalidCredentialsError
from src.app.schemas import (
    UserCreate,
    UserLogin,
)
from src.app.service import UserService


def create_user_for_tests(db_session, username, email, password):
    user_service = UserService(db_session)

    user_data = UserCreate(
        username=username,
        email=email,
        password=password,
    )

    user = user_service.create_user(user_data)

    return user


def test_create_account(db_session):
    response = create_user_for_tests(db_session, username="user", email="example@test.py", password="qwerty")

    assert response.email == "example@test.py"
    assert response.password_hash != "qwerty"
    assert response.role == "user"


def test_login_user(db_session):
    user_service = UserService(db_session)

    create_user_for_tests(db_session, username="user", email="example@test.py", password="qwerty")

    user_login_data = UserLogin(
        username="user",
        password="qwerty",
    )
    response = user_service.login_user(user_login_data)

    assert response.access_token is not None
    assert response.token_type == "bearer"


def test_login_user_with_wrong_password(db_session):
    user_service = UserService(db_session)

    create_user_for_tests(db_session, username="user", email="example@test.py", password="qwerty")

    user_login_data = UserLogin(
        username="user",
        password="ytrewq",
    )

    with pytest.raises(InvalidCredentialsError):
        user_service.login_user(user_login_data)


def test_users_with_identical_passwords(db_session):
    response_create_first = create_user_for_tests(db_session, username="user1", email="example_1@test.py", password="qwerty")
    response_create_second = create_user_for_tests(db_session, username="user2", email="example_2@test.py", password="qwerty")

    password_hash_first = response_create_first.password_hash
    password_hash_second = response_create_second.password_hash

    assert password_hash_first != password_hash_second
