from sqlalchemy import ForeignKey, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from datetime import datetime

from src.app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(unique=True, nullable=False)

    password_hash: Mapped[str]

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Room(Base):
    __tablename__ = "rooms"

    __table_args__ = (
        CheckConstraint(
            "capacity > 0",
            name="ck_rooms_capacity_positive"
        ),
    )

    room_id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str]

    capacity: Mapped[int]


class Booking(Base):
    __tablename__ = "bookings"

    booking_id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.room_id"))

    start_at: Mapped[datetime] = mapped_column()

    end_at: Mapped[datetime] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (
            CheckConstraint(
                "start_at < end_at",
                name="ck_bookings_time_range"
            ),
            ExcludeConstraint(
                ("room_id", "="),
                (func.tsrange(start_at, end_at, "[)"), "&&"),
                using="gist",
                name="no_overlapping_bookings"
            )
        )
