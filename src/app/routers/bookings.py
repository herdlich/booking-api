from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from typing import Annotated

from src.app.schemas import BookingCreate, BookingResponse, BookingDelete
from src.app.models import User
from src.app.service import get_current_user, create_booking, delete_booking, get_my_bookings
from src.app.database import get_session

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("", response_model=BookingResponse, summary="Create booking")
def create_booking_endpoint(data: BookingCreate, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_user)]):
    booking = create_booking(session, data, current_user.user_id)
    return booking


@router.get("/my", response_model=list[BookingResponse], summary="Show my bookings")
def get_my_bookings_endpoint(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_user)]):
    bookings = get_my_bookings(session, current_user.user_id)
    return bookings


@router.delete("/{booking_id}", summary="Delete booking")
def delete_booking_endpoint(booking_id: int, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_user)]):
    delete_booking(session = session, booking_id = booking_id, user_id = current_user.user_id)
    return {"status": "success", "message": "booking deleted"}
