from fastapi import FastAPI

from src.app.routers import users, bookings, rooms

app = FastAPI(
    title="Booking API",
    description="Room booking API Project",
    version="beta"
)

app.include_router(users.router)
app.include_router(bookings.router)
app.include_router(rooms.router)
