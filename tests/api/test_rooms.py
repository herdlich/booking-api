# =========================================================
#                        HAPPY PATH
# =========================================================
def test_create_room_endpoint(client, as_admin):
    payload = {
        "name": "Test Room",
        "capacity": 10,
    }

    response = client.post("/rooms", json=payload)
    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test Room"
    assert data["capacity"] == 10


def test_delete_room_endpoint(client, as_admin):
    payload = {
        "name": "Test Room",
        "capacity": 10,
    }

    response = client.post("/rooms", json=payload)
    assert response.status_code == 200

    room_id = response.json()["room_id"]

    response_delete = client.delete(f"/rooms/{room_id}")
    assert response_delete.status_code == 200

    assert response_delete.json() == {
        "status": "success",
        "message": "room deleted",
    }


def test_get_all_rooms_endpoint(client, as_admin):
    for i in range(1, 3):
        payload = {
            "name": f"Test Room {i}",
            "capacity": 10,
        }

        response = client.post("/rooms", json=payload)
        assert response.status_code == 200

    response_get_all = client.get("/rooms")
    assert response_get_all.status_code == 200

    data = response_get_all.json()

    assert data[0]["name"] == "Test Room 1"
    assert data[1]["name"] == "Test Room 2"


# =========================================================
#                         SAD PATH
# =========================================================
def test_no_permission_to_create_room_error(client, as_user):
    payload_for_create_room = {
        "name": "Test Room",
        "capacity": 10,
    }

    response_create_room = client.post("/rooms", json=payload_for_create_room)
    assert response_create_room.status_code == 403


def test_delete_room_with_incorrect_room_id_error(client, as_admin):
    payload_for_create_room = {
        "name": "Test Room",
        "capacity": 10,
    }

    response_create_room = client.post("/rooms", json=payload_for_create_room)
    assert response_create_room.status_code == 200

    incorrect_room_id = response_create_room.json()["room_id"] + 111

    response_delete_room = client.delete(f"/rooms/{incorrect_room_id}")
    assert response_delete_room.status_code == 404


def test_no_permission_to_delete_room_error(client, as_user):
    response_delete_room = client.delete("/rooms/111")
    assert response_delete_room.status_code == 403
