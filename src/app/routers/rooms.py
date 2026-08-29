from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from typing import Annotated

from src.app.schemas import RoomCreate, RoomResponse
from src.app.models import Room
from src.app.service import create_room
from src.app.database import get_session

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.post("", response_model=RoomResponse, summary="Room create")
def create_room_endpoint(data: RoomCreate, session: Annotated[Session, Depends(get_session)]):
    room = create_room(session, data)
    return room
