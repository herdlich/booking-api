from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.app import models
from src.app.exceptions import (
    EmailAlreadyExistsError,
    IncorrectBookingIdError,
    IncorrectRoomIdError,
    InvalidCredentialsError,
    NoPermissionToCreateRoomError,
    NoPermissionToDeleteBookingError,
    NoPermissionToDeleteRoomError,
    TimeOverlapError,
    UnauthorizedError,
)
from src.app.schemas import (
    BookingCreate,
    RoomCreate,
    TokenResponse,
    UserCreate,
    UserLogin,
)
from src.app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class UserService:
    def __init__(self, session):
        self.session = session

    def create_user(self, data: UserCreate) -> models.User:
        try:
            statement = select(models.User).where(models.User.email == data.email)
            existing_user = self.session.scalar(statement)

            if existing_user is not None:
                raise EmailAlreadyExistsError

            password_hash = hash_password(data.password)

            user = models.User(email=data.email, password_hash=password_hash)

            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)

            return user

        except Exception:
            self.session.rollback()
            raise

    def login_user(self, data: UserLogin) -> TokenResponse:
        statement = select(models.User).where(models.User.email == data.email)
        user = self.session.scalar(statement)

        if not user or not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsError

        token = create_access_token(user.user_id)

        return TokenResponse(access_token=token, token_type="bearer")

    def get_user_from_token(
            self,
            token: str,
    ) -> models.User:
        user_id = decode_access_token(token)

        statement = select(models.User).where(models.User.user_id == user_id)
        user = self.session.scalar(statement)

        if not user:
            raise UnauthorizedError

        return user


class RoomService:
    def __init__(self, session):
        self.session = session

    def create_room(self, data: RoomCreate, current_user: models.User) -> models.Room:
        try:
            if current_user.role != "admin":
                raise NoPermissionToCreateRoomError

            room = models.Room(name=data.name, capacity=data.capacity)

            self.session.add(room)
            self.session.commit()
            self.session.refresh(room)

            return room

        except Exception:
            self.session.rollback()
            raise

    def get_all_rooms(self):
        statement = select(models.Room)
        rooms = self.session.scalars(statement).all()

        return rooms

    def delete_room(self, room_id: int, current_user: models.User):
        try:
            if current_user.role != "admin":
                raise NoPermissionToDeleteRoomError

            statement = select(models.Room).where(models.Room.room_id == room_id)
            room = self.session.scalar(statement)

            if not room:
                raise IncorrectRoomIdError

            self.session.delete(room)
            self.session.commit()

        except Exception:
            self.session.rollback()
            raise


class BookingService:
    def __init__(self, session):
        self.session = session

    def create_booking(
            self,
            data: BookingCreate, user_id: int
    ) -> models.Booking:
        try:
            room_id = self.session.get(models.Room, data.room_id)

            if not room_id:
                raise IncorrectRoomIdError

            overlap_condition = select(models.Booking).where(
                models.Booking.room_id == data.room_id,
                data.start_at < models.Booking.end_at,
                data.end_at > models.Booking.start_at,
            ).exists()

            statement = select(overlap_condition)

            overlap_exists = self.session.scalar(statement)

            if overlap_exists:
                raise TimeOverlapError

            new_booking = models.Booking(
                user_id=user_id,
                room_id=data.room_id,
                start_at=data.start_at,
                end_at=data.end_at,
            )

            self.session.add(new_booking)

            self.session.commit()
            self.session.refresh(new_booking)

            return new_booking

        except IntegrityError as exc:
            self.session.rollback()

            constraint_name = getattr(
                getattr(exc.orig, "diag", None),
                "constraint_name",
                None,
            )

            if constraint_name == "no_overlapping_bookings":
                raise TimeOverlapError from exc

            raise

        except Exception:
            self.session.rollback()
            raise

    def get_my_bookings(self, user_id: int):
        statement = select(models.Booking).where(models.Booking.user_id == user_id)
        bookings = self.session.scalars(statement).all()

        return bookings

    def delete_booking(self, booking_id: int, user_id: int):
        try:
            statement = select(models.Booking).where(
                models.Booking.booking_id == booking_id
            )
            booking = self.session.scalar(statement)
            if not booking:
                raise IncorrectBookingIdError

            user_id_from_booking = booking.user_id

            if user_id != user_id_from_booking:
                raise NoPermissionToDeleteBookingError

            self.session.delete(booking)
            self.session.commit()

        except Exception:
            self.session.rollback()
            raise
