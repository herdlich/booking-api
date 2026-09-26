import os
import sys
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.app import models
from src.app.security import create_access_token

load_dotenv(".env")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


def create_user_for_tests(db_session, username, email, role):
    user = models.User(
        username=username,
        email=email,
        password_hash="argon2-hashedpass",
        role=role
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


# =========================================================
#                        HAPPY PATH
# =========================================================
def test_valid_token_returns_200(client, db_session):
    user = create_user_for_tests(db_session, "user", "example@test.py", "user")

    token = create_access_token(user.user_id)

    response = client.get(
        "/bookings/my",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


# =========================================================
#                         SAD PATH
# =========================================================
def test_invalid_token_returns_401(client):
    response = client.get(
        "/bookings/my",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_expired_token(client):
    payload = {
        "sub": "1",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    response = client.get(
        "/bookings/my",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_valid_admin_token_returns_200(client, db_session):
    user = create_user_for_tests(db_session, "admin", "admin@test.py", "admin")

    token = create_access_token(user.user_id)

    payload_room = {
        "name": "Test Room",
        "capacity": 10,
    }

    response = client.post(
        "/rooms",
        headers={"Authorization": f"Bearer {token}"},
        json=payload_room,
    )
    
    assert response.status_code == 200


def test_admin_router_with_user_token_returns_403(client, db_session):
    user = create_user_for_tests(db_session, "user", "admin@test.py", "user")

    token = create_access_token(user.user_id)

    payload_room = {
        "name": "Test Room",
        "capacity": 10,
    }

    response = client.post(
        "/rooms",
        headers={"Authorization": f"Bearer {token}"},
        json=payload_room,
    )

    assert response.status_code == 403
