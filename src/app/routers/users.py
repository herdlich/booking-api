from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated

from src.app.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from src.app.models import User
from src.app.service import create_user, login_user
from src.app.database import get_session

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, summary="Sign up")
def create_user_endpoint(data: UserCreate, session: Annotated[Session, Depends(get_session)]):
    return create_user(session, data)


@router.post("/login", response_model=TokenResponse, summary="Sign in")
def login_user_endpoint(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Session, Depends(get_session)]):
    user_login = UserLogin(email=form_data.username, password=form_data.password)
    return login_user(session, user_login)
