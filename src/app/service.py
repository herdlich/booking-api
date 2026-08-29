from sqlalchemy.orm import Session
from sqlalchemy import select, exists

from typing import Annotated
from fastapi import Depends

from src.app import models
from src.app.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    RoomCreate,
    RoomResponse,
    BookingCreate,
    BookingResponse,
    TokenResponse,
)
from src.app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    oauth2_scheme,
)
from src.app.database import get_session
from src.app.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UnauthorizedError,
    IncorrectRoomIdError,
    TimeOverlapError,
    IncorrectBookingIdError,
    NoPermissionToDeleteBookingError,
)


def create_user(session: Session, data: UserCreate) -> models.User:
    try:
        statement = select(models.User).where(models.User.email == data.email)
        existing_user = session.scalar(statement)

        if existing_user is not None:
            raise EmailAlreadyExistsError

        password_hash = hash_password(data.password)

        user = models.User(email=data.email, password_hash=password_hash)

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    except Exception:
        session.rollback()
        raise


def login_user(session: Session, data: UserLogin) -> TokenResponse:
    statement = select(models.User).where(models.User.email == data.email)
    user = session.scalar(statement)

    if not user or not verify_password(data.password, user.password_hash):
        raise InvalidCredentialsError

    token = create_access_token(user.user_id)

    return TokenResponse(access_token=token, token_type="bearer")


def get_current_user(
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> models.User:
    user_id = decode_access_token(token)

    statement = select(models.User).where(models.User.user_id == user_id)
    user = session.scalar(statement)

    if not user:
        raise UnauthorizedError

    return user


def create_room(session: Session, data: RoomCreate) -> models.Room:
    try:
        room = models.Room(name=data.name, capacity=data.capacity)

        session.add(room)
        session.commit()
        session.refresh(room)

        return room

    except Exception:
        session.rollback()
        raise


def get_all_rooms(session: Session):
    statement = select(models.Room)
    rooms = session.scalars(statement).all()

    return rooms


def delete_room(session: Session, room_id: int):
    try:
        statement = select(models.Room).where(models.Room.room_id == room_id)
        room = session.scalar(statement)

        if not room:
            raise IncorrectRoomIdError

        session.delete(room)
        session.commit()

    except Exception:
        session.rollback()
        raise


def create_booking(
    session: Session, data: BookingCreate, user_id: int
) -> models.Booking:
    try:
        room_id = session.get(models.Room, data.room_id)

        if not room_id:
            raise IncorrectRoomIdError

        overlap_condition = select(models.Booking).where(
                models.Booking.room_id == data.room_id,
                data.start_at < models.Booking.end_at,
                data.end_at > models.Booking.start_at,
            ).exists()

        statement = select(overlap_condition)

        overlap_exists = session.scalar(statement)

        if overlap_exists:
            raise TimeOverlapError

        new_booking = models.Booking(
            user_id=user_id,
            room_id=data.room_id,
            start_at=data.start_at,
            end_at=data.end_at,
        )

        session.add(new_booking)

        session.commit()
        session.refresh(new_booking)

        return new_booking

    except Exception:
        session.rollback()
        raise


def get_my_bookings(session: Session, user_id: int):
    statement = select(models.Booking).where(models.Booking.user_id == user_id)
    bookings = session.scalars(statement).all()

    return bookings


def delete_booking(session: Session, booking_id: int, user_id: int):
    try:
        statement = select(models.Booking).where(
            models.Booking.booking_id == booking_id
        )
        booking = session.scalar(statement)
        if not booking:
            raise IncorrectBookingIdError

        user_id_from_booking = booking.user_id

        if user_id != user_id_from_booking:
            raise NoPermissionToDeleteBookingError

        session.delete(booking)
        session.commit()

    except Exception:
        session.rollback()
        raise
