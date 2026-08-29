from fastapi import FastAPI

from app.routers import users, bookings

app = FastAPI(
    title="Booking API",
    description="Room booking API Project",
    version="beta"
)

app.include_router(users.router)
app.include_router(bookings.router)
