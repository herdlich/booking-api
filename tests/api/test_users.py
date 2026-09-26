import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# =========================================================
#                        HAPPY PATH
# =========================================================
def test_create_user_endpoint(client):
    payload = {
        "username": "user",
        "email": "example@test.py",
        "password": "qwerty",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 200

    data = response.json()

    date = datetime.fromisoformat(data["created_at"])

    assert isinstance(data["user_id"], int)
    assert data["email"] == "example@test.py"
    assert isinstance(date, datetime)


def test_login_user_endpoint(client):
    payload = {
        "username": "user",
        "email": "example@test.py",
        "password": "qwerty",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 200

    payload_login = {
        "username": "user",
        "password": "qwerty",
    }

    response_login = client.post("/auth/login", data=payload_login)

    assert response_login.status_code == 200

    data = response_login.json()

    assert isinstance(data["access_token"], str)
    assert data["token_type"] == "bearer"


# =========================================================
#                         SAD PATH
# =========================================================
def test_create_user_with_email_already_exists_error(client):
    payload = {
        "username": "user",
        "email": "example@test.py",
        "password": "qwerty",
    }

    response_first = client.post("/auth/register", json=payload)
    assert response_first.status_code == 200

    response_second = client.post("/auth/register", json=payload)
    assert response_second.status_code == 409


def test_login_user_with_invalid_credentials_error(client):
    payload_for_create = {
        "username": "user",
        "email": "example@test.py",
        "password": "qwerty",
    }

    response_create_user = client.post("/auth/register", json=payload_for_create)
    assert response_create_user.status_code == 200

    payload_for_login_wrong_password = {
        "username": "user",
        "password": "ytrewq",
    }

    response_login_user_wrong_password = client.post("/auth/login", data=payload_for_login_wrong_password)
    assert response_login_user_wrong_password.status_code == 401

    payload_for_login_non_existent_username = {
        "username": "resu",
        "password": "qwerty",
    }

    response_login_user_non_existent_email = client.post("/auth/login", data=payload_for_login_non_existent_username)
    assert response_login_user_non_existent_email.status_code == 401
