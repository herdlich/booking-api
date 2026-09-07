import sys
import os

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
