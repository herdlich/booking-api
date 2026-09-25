from fastapi import Depends, APIRouter, HTTPException
from typing import Annotated

from src.app.schemas import BookingCreate, BookingResponse
from src.app.models import User
from src.app.service import BookingService, UserService
from src.app.dependencies import get_booking_service, get_current_user
from src.app.exceptions import (
    IncorrectRoomIdError,
    TimeOverlapError,
    IncorrectBookingIdError,
    NoPermissionToDeleteBookingError,
)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("", response_model=BookingResponse, summary="Create Booking")
def create_booking_endpoint(
        data: BookingCreate,
        service: Annotated[BookingService, Depends(get_booking_service)],
        current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        booking = service.create_booking(session, data, current_user.user_id)
        return booking

    except IncorrectRoomIdError:
        raise HTTPException(
            status_code=404,
            detail="This Room ID does not exist",
        )

    except TimeOverlapError:
        raise HTTPException(
            status_code=409,
            detail="Booking overlaps with another one",
        )


@router.get("/my", response_model=list[BookingResponse], summary="Show My Bookings")
def get_my_bookings_endpoint(
        service: Annotated[BookingService, Depends(get_booking_service)],
        current_user: Annotated[User, Depends(get_current_user)],
):
    bookings = service.get_my_bookings(session, current_user.user_id)
    return bookings


@router.delete("/{booking_id}", summary="Delete Booking")
def delete_booking_endpoint(
        booking_id: int,
        service: Annotated[BookingService, Depends(get_booking_service)],
        current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        service.delete_booking(session=session, booking_id=booking_id, user_id=current_user.user_id)
        return {"status": "success", "message": "booking deleted"}

    except IncorrectBookingIdError:
        raise HTTPException(
            status_code=404,
            detail="This Booking ID does not exist",
        )

    except NoPermissionToDeleteBookingError:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own booking",
        )
