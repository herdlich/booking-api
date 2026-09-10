import os
import sys
import pytest
from sqlalchemy.exc import IntegrityError

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.app import models

# =========================================================
#                        HAPPY PATH
# =========================================================
def test_create_room_in_database(db_session):
    room = models.Room(
        name="Test Room",
        capacity=10,
    )

    db_session.add(room)
    db_session.commit()
    db_session.refresh(room)

    assert room.name == "Test Room"
    assert room.capacity == 10


# =========================================================
#                         SAD PATH
# =========================================================
def test_create_room_with_null_capacity_in_database(db_session):
    room = models.Room(
        name="Test Room",
        capacity=0,
    )

    with pytest.raises(IntegrityError):
        db_session.add(room)
        db_session.commit()
