from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.app.dependencies import get_current_user, get_room_service
from src.app.exceptions import (
    IncorrectRoomIdError,
    NoPermissionToCreateRoomError,
    NoPermissionToDeleteRoomError,
)
from src.app.models import User
from src.app.schemas import RoomCreate, RoomResponse
from src.app.service import RoomService

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.post("", response_model=RoomResponse, summary="Create Room")
def create_room_endpoint(
        data: RoomCreate,
        service: Annotated[RoomService, Depends(get_room_service)],
        current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        room = service.create_room(data, current_user)
        return room

    except NoPermissionToCreateRoomError:
        raise HTTPException(
            status_code=403,
            detail="You dont have the required permissions"
        )


@router.get("", response_model=list[RoomResponse], summary="List Rooms")
def get_all_rooms_endpoint(service: Annotated[RoomService, Depends(get_room_service)]):
    return service.get_all_rooms()


@router.delete("/{room_id}", summary="Delete Room")
def delete_room_endpoint(
        room_id: int,
        service: Annotated[RoomService, Depends(get_room_service)],
        current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        service.delete_room(room_id, current_user)
        return {"status": "success", "message": "room deleted"}

    except IncorrectRoomIdError:
        raise HTTPException(
            status_code=404,
            detail="This Room ID does not exist",
        )

    except NoPermissionToDeleteRoomError:
        raise HTTPException(
            status_code=403,
            detail="You dont have the required permissions"
        )
