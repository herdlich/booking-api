import sys
import os
from sqlalchemy import select
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.app.service import (
    create_booking,
    delete_booking,
    get_my_bookings,
    create_user,
    create_room,
)
from src.app.schemas import (
    BookingCreate,
    RoomCreate,
    UserCreate,
)
from src.app.models import Booking


def create_user_for_tests(db_session, email, password):
    user_data = UserCreate(
        email=email,
        password=password,
    )

    user = create_user(db_session, user_data)

    return user


def set_admin_for_tests(db_session, user):
    user.role = "admin"

    db_session.commit()
    db_session.refresh(user)

    return user


def create_room_for_tests(db_session, admin):
    room_data = RoomCreate(
        name="Test Room",
        capacity=10,
    )

    room = create_room(db_session, room_data, admin)

    return room


def create_booking_for_tests(db_session, user_id, room_id, start_at, end_at):
    booking_data = BookingCreate(
        room_id=room_id,
        start_at=start_at,
        end_at=end_at,
    )

    booking = create_booking(db_session, booking_data, user_id)

    return booking


def test_create_booking(db_session):
    user = create_user_for_tests(db_session, email="admin@test.py", password="qwerty")
    admin = set_admin_for_tests(db_session, user)
    user_id = admin.user_id

    room = create_room_for_tests(db_session, admin)
    room_id = room.room_id

    start_at = datetime.fromisoformat("1999-12-31T23:00:00")
    end_at = datetime.fromisoformat("2000-01-01T00:00:00")

    booking = BookingCreate(
        room_id=room_id,
        start_at=start_at,
        end_at=end_at,
    )
    response = create_booking(db_session, booking, user_id)

    assert response.room_id == room_id
    assert response.start_at == start_at
    assert response.end_at == end_at


def test_get_my_bookings(db_session):
    user = create_user_for_tests(db_session, "admin@test.py", "qwerty")
    admin = set_admin_for_tests(db_session, user)
    user_id = admin.user_id

    room = create_room_for_tests(db_session, admin)
    room_id = room.room_id

    start_at_first = datetime.fromisoformat("1999-12-31T23:00:00")
    end_at_first = datetime.fromisoformat("2000-01-01T00:00:00")

    first_booking = create_booking_for_tests(db_session, user_id, room_id, start_at_first, end_at_first)

    start_at_second = datetime.fromisoformat("2099-12-31T23:00:00")
    end_at_second = datetime.fromisoformat("2100-01-01T00:00:00")

    second_booking = create_booking_for_tests(db_session, user_id, room_id, start_at_second, end_at_second)

    assert first_booking is not None
    assert second_booking is not None

    response = get_my_bookings(db_session, user_id)

    assert response[0].room_id == room_id
    assert response[1].room_id == room_id

    assert response[0].start_at == start_at_first
    assert response[0].end_at == end_at_first

    assert response[1].start_at == start_at_second
    assert response[1].end_at == end_at_second


def test_delete_booking(db_session):
    user = create_user_for_tests(db_session, "admin@test.py", "qwerty")
    admin = set_admin_for_tests(db_session, user)
    user_id = admin.user_id

    room = create_room_for_tests(db_session, admin)
    room_id = room.room_id

    start_at = datetime.fromisoformat("1999-12-31T23:00:00")
    end_at = datetime.fromisoformat("2000-01-01T00:00:00")

    booking = create_booking_for_tests(db_session, user_id, room_id, start_at, end_at)

    assert booking.user_id == user_id
    assert booking.room_id == room_id
    assert booking.start_at == start_at
    assert booking.end_at == end_at

    booking_id = booking.booking_id

    delete_booking(db_session, booking_id, user_id)

    statement = select(Booking).where(Booking.booking_id == booking_id)
    booking_no_exist = db_session.scalar(statement)

    assert booking_no_exist is None
