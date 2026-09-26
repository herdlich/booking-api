from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.app.dependencies import get_user_service
from src.app.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from src.app.schemas import TokenResponse, UserCreate, UserLogin, UserResponse
from src.app.service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, summary="Sign Up")
def create_user_endpoint(data: UserCreate,
                         service: Annotated[UserService, Depends(get_user_service)]):
    try:
        return service.create_user(data)
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="User with this email already exists",
        )


@router.post("/login", response_model=TokenResponse, summary="Sign In")
def login_user_endpoint(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                        service: Annotated[UserService, Depends(get_user_service)]):
    try:
        user_login = UserLogin(username=form_data.username, password=form_data.password)
        return service.login_user(user_login)

    except InvalidCredentialsError:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )
