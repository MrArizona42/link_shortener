from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

from app.auth.models import UserCreds, UserGetResponse
from app.config import settings
from app.db import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def _authenticate_or_register_user(email: str, password: str, database) -> dict:
    """Handles user authentication and registration logic."""
    sql_get_user = "app/auth/sql/get_user.sql"
    response = await database.fetch(sql_get_user, email)

    if not response:
        # New user registration
        hashed_password = get_password_hash(password)
        token = create_access_token(
            data={"sub": email}, expires_delta=timedelta(minutes=60)
        )
        sql_create_user = "app/auth/sql/create_user.sql"
        response = await database.fetch(sql_create_user, email, hashed_password, token)
    else:
        # Existing user authentication
        hashed_password = response[0]["hashed_password"]
        if not verify_password(password, hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")

        # Generate a fresh token for login
        token = create_access_token(
            data={"sub": email}, expires_delta=timedelta(minutes=60)
        )

    return {
        "id": response[0]["id"],
        "email": response[0]["email"],
        "token": token,
        "created_at": response[0]["created_at"],
    }


@router.post("/get_token", response_model=UserGetResponse)
async def register(user: UserCreds, database=Depends(get_db)):
    user_data = await _authenticate_or_register_user(
        user.email, user.password, database
    )
    return UserGetResponse(**user_data)


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), database=Depends(get_db)
):
    user_data = await _authenticate_or_register_user(
        form_data.username, form_data.password, database
    )
    return {"access_token": user_data["token"], "token_type": "bearer"}
