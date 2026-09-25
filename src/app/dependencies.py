from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.app.database import get_session
from src.app.security import oauth2_scheme
from src.app.service import BookingService, RoomService, UserService


def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Annotated[Session, Depends(get_session)],
):
    service = UserService(session)
    return service.get_user_from_token(token)


def get_user_service(
        session: Annotated[Session, Depends(get_session)],
) -> UserService:
    return UserService(session)


def get_room_service(
        session: Annotated[Session, Depends(get_session)],
) -> RoomService:
    return RoomService(session)


def get_booking_service(
        session: Annotated[Session, Depends(get_session)],
) -> BookingService:
    return BookingService(session)
