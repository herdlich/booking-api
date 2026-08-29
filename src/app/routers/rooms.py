from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

from src.app.schemas import RoomCreate, RoomResponse
from src.app.service import create_room, get_all_rooms, delete_room
from src.app.database import get_session
from src.app.exceptions import IncorrectRoomIdError

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.post("", response_model=RoomResponse, summary="Create Room")
def create_room_endpoint(data: RoomCreate, session: Annotated[Session, Depends(get_session)]):
    room = create_room(session, data)
    return room


@router.get("", response_model=list[RoomResponse], summary="List Rooms")
def get_all_rooms_endpoint(session: Annotated[Session, Depends(get_session)]):
    return get_all_rooms(session)


@router.delete("/{room_id}", summary="Delete Room")
def delete_room_endpoint(room_id: int, session: Annotated[Session, Depends(get_session)]):
    try:
        delete_room(session, room_id)
        return {"status": "success", "message": "booking deleted"}
    except IncorrectRoomIdError:
        raise HTTPException(
            status_code=404,
            detail="This Room ID does not exist",
        )
