import os
import sys

from sqlalchemy import select

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.app.models import Room, User
from src.app.schemas import (
    RoomCreate,
    UserCreate,
)
from src.app.service import RoomService, UserService


def create_user_for_tests(db_session, username, email, password):
    user_service = UserService(db_session)

    user_data = UserCreate(
        username=username,
        email=email,
        password=password,
    )

    user = user_service.create_user(user_data)

    return user


def set_admin_for_tests(db_session, user):
    statement = select(User).where(User.email == user.email)
    user = db_session.scalar(statement)

    user.role = "admin"

    db_session.commit()
    db_session.refresh(user)

    return user


def test_create_room_with_admin(db_session):
    room_service = RoomService(db_session)

    user = create_user_for_tests(db_session, username="admin", email="admin@test.py", password="qwerty")
    admin = set_admin_for_tests(db_session, user)

    room_data = RoomCreate(
        name="Test Room",
        capacity=10,
    )

    response = room_service.create_room(room_data, admin)

    assert response.name == "Test Room"
    assert response.capacity == 10


def test_delete_room_without_admin(db_session):
    room_service = RoomService(db_session)

    user = create_user_for_tests(db_session, username="admin", email="admin@test.py", password="qwerty")
    admin = set_admin_for_tests(db_session, user)

    room_data = RoomCreate(
        name="Test Room",
        capacity=10,
    )

    created_room = room_service.create_room(room_data, admin)

    assert created_room.name == "Test Room"
    assert created_room.capacity == 10

    room_id = created_room.room_id

    statement = select(Room).where(Room.room_id == room_id)
    room = db_session.scalar(statement)

    assert room.name == "Test Room"
    assert room.capacity == 10

    room_service.delete_room(room_id, admin)

    statement_deleted = select(Room).where(Room.room_id == room_id)
    deleted_room = db_session.scalar(statement_deleted)

    assert deleted_room is None


def test_get_all_rooms(db_session):
    room_service = RoomService(db_session)

    user = create_user_for_tests(db_session, username="admin", email="admin@test.py", password="qwerty")
    admin = set_admin_for_tests(db_session, user)

    for i in range(1, 3):
        room_data = RoomCreate(
            name=f"Test Room {i}",
            capacity=10 + i,
        )

        room_service.create_room(room_data, admin)

    all_rooms = room_service.get_all_rooms()

    assert len(all_rooms) == 2

    assert all_rooms[0].name == "Test Room 1"
    assert all_rooms[1].name == "Test Room 2"

    assert all_rooms[0].capacity == 11
    assert all_rooms[1].capacity == 12
