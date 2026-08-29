from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator
from datetime import datetime


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RoomCreate(BaseModel):
    name: str
    capacity: int = Field(gt=0, description="Capacity must be greater than 0")


class BookingCreate(BaseModel):
    room_id: int
    start_at: datetime
    end_at: datetime

    @model_validator(mode="after")
    def validate_dates(self) -> "BookingCreate":
        if self.start_at >= self.end_at:
            raise ValueError("The start date must be earlier than the end date")
        return self


class UserResponse(SchemaBase):
    user_id: int
    email: str
    created_at: datetime


class RoomResponse(SchemaBase):
    room_id: int
    name: str
    capacity: int


class BookingResponse(SchemaBase):
    booking_id: int
    user_id: int
    room_id: int
    start_at: datetime
    end_at: datetime
    created_at: datetime


class BookingDelete(BaseModel):
    booking_id: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
