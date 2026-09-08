import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_create_user_endpoint(client):
    payload = {
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


def test_create_existing_user_endpoint(client):
    payload = {
        "email": "example@test.py",
        "password": "qwerty",
    }

    response_first = client.post("/auth/register", json=payload)
    assert response_first.status_code == 200

    response_second = client.post("/auth/register", json=payload)
    assert response_second.status_code == 409


def test_login_user_endpoint(client):
    payload = {
        "email": "example@test.py",
        "password": "qwerty",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 200

    payload_login = {
        "username": "example@test.py",
        "password": "qwerty",
    }

    response_login = client.post("/auth/login", data=payload_login)

    assert response_login.status_code == 200

    data = response_login.json()

    assert isinstance(data["access_token"], str)
    assert data["token_type"] == "bearer"
