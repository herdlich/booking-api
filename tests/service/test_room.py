import sys
import os
from sqlalchemy import select

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.app.service import (
    create_room,
    delete_room,
    get_all_rooms,
    create_user,
)
from src.app.schemas import (
    RoomCreate,
    UserCreate,
)
from src.app.models import User, Room


def create_user_for_tests(db_session, email, password):
    user_data = UserCreate(
        email=email,
        password=password,
    )

    user = create_user(db_session, user_data)

    return user


def set_admin_for_tests(db_session):
    create_user_for_tests(db_session, "admin@test.py", "qwerty")

    statement = select(User).where(User.email == "admin@test.py")
    user = db_session.scalar(statement)

    user.role = "admin"

    db_session.commit()
    db_session.refresh(user)

    return user


def test_create_room_with_admin(db_session):
    admin = set_admin_for_tests(db_session)

    room_data = RoomCreate(
        name="Test Room",
        capacity=10,
    )

    response = create_room(db_session, room_data, admin)

    assert response.name == "Test Room"
    assert response.capacity == 10


def test_delete_room_without_admin(db_session):
    admin = set_admin_for_tests(db_session)

    room_data = RoomCreate(
        name="Test Room",
        capacity=10,
    )

    created_room = create_room(db_session, room_data, admin)

    assert created_room.name == "Test Room"
    assert created_room.capacity == 10

    room_id = created_room.room_id

    statement = select(Room).where(Room.room_id == room_id)
    room = db_session.scalar(statement)

    assert room.name == "Test Room"
    assert room.capacity == 10

    delete_room(db_session, room_id, admin)

    statement_deleted = select(Room).where(Room.room_id == room_id)
    deleted_room = db_session.scalar(statement_deleted)

    assert deleted_room is None


def test_get_all_rooms(db_session):
    admin = set_admin_for_tests(db_session)

    for i in range(1, 3):
        room_data = RoomCreate(
            name=f"Test Room {i}",
            capacity=10 + i,
        )

        create_room(db_session, room_data, admin)

    all_rooms = get_all_rooms(db_session)

    assert len(all_rooms) == 2

    assert all_rooms[0].name == "Test Room 1"
    assert all_rooms[1].name == "Test Room 2"

    assert all_rooms[0].capacity == 11
    assert all_rooms[1].capacity == 12
