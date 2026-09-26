import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.app import models


# =========================================================
#                        HAPPY PATH
# =========================================================
def create_room_for_tests(db_session, name, capacity):
    room = models.Room(
        name=name,
        capacity=capacity,
    )

    db_session.add(room)
    db_session.commit()
    db_session.refresh(room)

    return room


def create_fake_user_for_tests(db_session):
    user = models.User(
        username="fakeuser",
        email="fake@test.py",
        password_hash="argon2-hashedpass",

    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def create_booking_for_tests(db_session, user_id, room_id, start_at, end_at):
    booking = models.Booking(
        user_id=user_id,
        room_id=room_id,
        start_at=start_at,
        end_at=end_at,
    )

    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    return booking


def test_create_booking_endpoint(db_session, client, as_user):
    room = create_room_for_tests(db_session, "Test Room", 10)

    start_at = "1999-12-31T23:00:00"
    end_at = "2000-01-01T00:00:00"

    payload = {
        "room_id": room.room_id,
        "start_at": start_at,
        "end_at": end_at,
    }

    response = client.post("/bookings", json=payload)
    assert response.status_code == 200

    data = response.json()

    assert data["room_id"] == room.room_id
    assert data["start_at"] == start_at
    assert data["end_at"] == end_at


def test_delete_booking_endpoint(db_session, client, as_user):
    room = create_room_for_tests(db_session, "Test Room", 10)

    start_at = "1999-12-31T23:00:00"
    end_at = "2000-01-01T00:00:00"

    payload = {
        "room_id": room.room_id,
        "start_at": start_at,
        "end_at": end_at,
    }

    response = client.post("/bookings", json=payload)
    assert response.status_code == 200

    booking_id = response.json()["booking_id"]

    response_deleted = client.delete(f"/bookings/{booking_id}")
    assert response_deleted.status_code == 200

    data = response_deleted.json()

    assert data == {
        "status": "success",
        "message": "booking deleted",
    }


def test_get_my_bookings_endpoint(db_session, client, as_user):
    room = create_room_for_tests(db_session, "Test Room", 10)

    start_at = "1999-12-31T23:00:00"
    end_at = "2000-01-01T00:00:00"

    payload = {
        "room_id": room.room_id,
        "start_at": start_at,
        "end_at": end_at,
    }

    response = client.post("/bookings", json=payload)
    assert response.status_code == 200

    response_get_bookings = client.get("/bookings/my")
    assert response_get_bookings.status_code == 200

    data = response_get_bookings.json()

    assert data[0]["room_id"] == room.room_id
    assert data[0]["start_at"] == start_at
    assert data[0]["end_at"] == end_at


# =========================================================
#                         SAD PATH
# =========================================================
def test_create_booking_with_incorrect_room_id_error(db_session, client, as_user):
    start_at = "1999-12-31T23:00:00"
    end_at = "2000-01-01T00:00:00"

    payload_for_create_booking = {
        "room_id": 1,
        "start_at": start_at,
        "end_at": end_at,
    }

    response_create_booking = client.post("/bookings", json=payload_for_create_booking)
    assert response_create_booking.status_code == 404


def test_create_booking_with_time_overlap_error(db_session, client, as_user):
    room = create_room_for_tests(db_session, "Test Room", 10)

    start_at_first = "1999-12-31T23:00:00"
    end_at_first = "2000-01-01T00:00:00"

    payload_for_first_create_booking = {
        "room_id": room.room_id,
        "start_at": start_at_first,
        "end_at": end_at_first,
    }

    start_at_second = "1999-12-31T23:30:00"
    end_at_second = "2000-01-01T00:30:00"

    payload_for_second_create_booking = {
        "room_id": room.room_id,
        "start_at": start_at_second,
        "end_at": end_at_second,
    }

    response_first_create_booking = client.post("/bookings", json=payload_for_first_create_booking)
    assert response_first_create_booking.status_code == 200

    response_second_create_booking = client.post("/bookings", json=payload_for_second_create_booking)
    assert response_second_create_booking.status_code == 409


def test_delete_booking_with_incorrect_booking_id_error(client, as_user):
    response_delete_booking = client.delete("/bookings/1")
    assert response_delete_booking.status_code == 404


def test_no_permission_to_delete_booking_error(db_session, client, as_user):
    room = create_room_for_tests(db_session, "Test Room", 10)
    user = create_fake_user_for_tests(db_session)

    start_at = "1999-12-31T23:00:00"
    end_at = "2000-01-01T00:00:00"

    booking = create_booking_for_tests(db_session, user.user_id, room.room_id, start_at, end_at)

    response_delete_booking = client.delete(f"/bookings/{booking.booking_id}")
    assert response_delete_booking.status_code == 403
