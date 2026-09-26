import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Barrier

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.app import models


def create_room_for_tests(db_session, name, capacity):
    room = models.Room(
        name=name,
        capacity=capacity,
    )

    db_session.add(room)
    db_session.commit()
    db_session.refresh(room)

    return room


def create_user_for_tests(db_session, username, email):
    user = models.User(
        username=username,
        email=email,
        password_hash="argon2-hashedpass",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


# =========================================================
#                        HAPPY PATH
# =========================================================
def test_create_booking_in_database(db_session):
    room = create_room_for_tests(db_session, "Test Room", 10)
    user = create_user_for_tests(db_session, username="user", email="example@test.py")

    start_at = datetime.fromisoformat("1999-12-31T23:00:00")
    end_at = datetime.fromisoformat("2000-01-01T00:00:00")

    booking = models.Booking(
        user_id=user.user_id,
        room_id=room.room_id,
        start_at=start_at,
        end_at=end_at,
    )

    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    assert isinstance(booking.booking_id, int)
    assert booking.room_id == room.room_id
    assert booking.room_id == room.room_id


# =========================================================
#                         SAD PATH
# =========================================================
def test_create_booking_with_time_overlap_in_database(db_session):
    room = create_room_for_tests(db_session, "Test Room", 10)
    user = create_user_for_tests(db_session, username="user", email="example@test.py")

    start_at_first = datetime.fromisoformat("1999-12-31T23:00:00")
    end_at_first = datetime.fromisoformat("2000-01-01T00:00:00")

    booking_first = models.Booking(
        user_id=user.user_id,
        room_id=room.room_id,
        start_at=start_at_first,
        end_at=end_at_first,
    )

    start_at_second = datetime.fromisoformat("1999-12-31T23:00:00")
    end_at_second = datetime.fromisoformat("2000-01-01T00:00:00")

    booking_second = models.Booking(
        user_id=user.user_id,
        room_id=room.room_id,
        start_at=start_at_second,
        end_at=end_at_second,
    )

    db_session.add(booking_first)
    db_session.commit()

    with pytest.raises(IntegrityError):
        db_session.add(booking_second)
        db_session.commit()


def test_create_booking_with_incorrect_time_range(db_session):
    room = create_room_for_tests(db_session, "Test Room", 10)
    user = create_user_for_tests(db_session, username="user", email="example@test.py")

    start_at = datetime.fromisoformat("2000-01-01T00:00:00")
    end_at = datetime.fromisoformat("1999-12-31T23:00:00")

    booking = models.Booking(
        user_id=user.user_id,
        room_id=room.room_id,
        start_at=start_at,
        end_at=end_at,
    )

    with pytest.raises(IntegrityError):
        db_session.add(booking)
        db_session.commit()


def test_create_booking_with_time_overlap_at_the_same_time_in_database(test_engine, db_session):
    room = create_room_for_tests(db_session, "Test Room", 10)
    user = create_user_for_tests(db_session, username="user", email="example@test.py")

    start_at = datetime.fromisoformat("1999-12-31T23:00:00")
    end_at = datetime.fromisoformat("2000-01-01T00:00:00")

    SessionFactory = sessionmaker(bind=test_engine)

    barrier = Barrier(2)

    def make_booking():
        with SessionFactory() as session:
            barrier.wait()

            booking = models.Booking(
                user_id=user.user_id,
                room_id=room.room_id,
                start_at=start_at,
                end_at=end_at,
            )

            session.add(booking)

            try:
                session.commit()
                return "created"

            except IntegrityError as exc:
                constraint_name = getattr(
                    getattr(exc.orig, "diag", None),
                    "constraint_name",
                    None
                )

                if constraint_name == "no_overlapping_bookings":
                    return "conflict"

                raise

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                lambda _: make_booking(),
                range(2),
            )
        )

    assert sorted(results) == ["conflict", "created"]
