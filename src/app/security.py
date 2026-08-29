from pwdlib import PasswordHash

import jwt
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
import os

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

jwt_secret_key = os.getenv("JWT_SECRET_KEY")
jwt_algorithm = os.getenv("JWT_ALGORITHM")

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=2)

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    token = jwt.encode(payload, jwt_secret_key, algorithm=jwt_algorithm)

    return token


def decode_access_token(token: str) -> int:
    payload = jwt.decode(token, jwt_secret_key, algorithms=[jwt_algorithm])

    user_id = payload.get("sub")
    if not user_id:
        raise RuntimeError("Error sub")
    
    if not user_id.isdigit():
        raise RuntimeError("Uncorrect User-ID result")

    return int(user_id)
