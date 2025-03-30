from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.models import TokenUpdateResponse, UserCreds, UserGetResponse
from app.config import settings
from app.db import get_db

router = APIRouter()


def get_password_hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def _authenticate_or_register_user(email: str, password: str, database) -> dict:
    sql_get_user = "app/auth/sql/get_user.sql"
    response = await database.fetch(sql_get_user, email)

    if not response:
        # New user registration
        if len(password) < 8:
            raise HTTPException(
                status_code=422,
                detail="Password must be at least 8 characters long",
            )
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

    return {
        "id": response[0]["id"],
        "email": response[0]["email"],
        "token": response[0]["token"],
        "created_at": response[0]["created_at"],
        "updated_at": response[0]["updated_at"],
    }


@router.post("/get_token", response_model=UserGetResponse)
async def register(user: UserCreds, database=Depends(get_db)):
    user_data = await _authenticate_or_register_user(
        user.email, user.password, database
    )
    return UserGetResponse(**user_data)


@router.post("/update_token", response_model=TokenUpdateResponse)
async def update_token(user: UserCreds, database=Depends(get_db)):
    sql_get_user = "app/auth/sql/get_user.sql"

    response = await database.fetch(sql_get_user, user.email)
    if not response:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = response[0]["hashed_password"]
    if not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=60)
    )

    sql_update_token = "app/auth/sql/update_token.sql"
    response = await database.fetch(sql_update_token, user.email, token)
    user_data = response[0]

    return TokenUpdateResponse(**user_data)


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), database=Depends(get_db)
):
    user_data = await _authenticate_or_register_user(
        form_data.username, form_data.password, database
    )
    return {"access_token": user_data["token"], "token_type": "bearer"}
