from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.app.exceptions import UnauthorizedError
from src.app.routers import bookings, rooms, users

app = FastAPI(
    title="Booking API",
    description="Room booking API Project",
    version="beta"
)

@app.exception_handler(UnauthorizedError)
def unauthorized_handler(
        _request: Request,
        _exc: UnauthorizedError,
):
    return JSONResponse(
        status_code=401,
        content={"detail": "Unauthorized"},
        headers={"WWW-Authenticate": "Bearer"},
    )

app.include_router(users.router)
app.include_router(bookings.router)
app.include_router(rooms.router)
