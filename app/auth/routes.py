from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
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


@router.post("/get_token", response_model=UserGetResponse)
async def register(user: UserCreds, database=Depends(get_db)):
    sql_get_user = "app/auth/sql/get_user.sql"

    response = await database.fetch(sql_get_user, user.email)
    if not response:
        # ----- New user flow -----
        hashed_password = get_password_hash(user.password)
        token = create_access_token(
            data={"sub": user.email}, expires_delta=timedelta(minutes=60)
        )
        sql_create_user = "app/auth/sql/create_user.sql"
        response = await database.fetch(
            sql_create_user, user.email, hashed_password, token
        )
    else:
        # ----- Existing user password check -----
        hashed_password = response[0]["hashed_password"]
        if not verify_password(user.password, hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")

    return UserGetResponse(
        id=response[0]["id"],
        email=response[0]["email"],
        token=response[0]["token"],
        created_at=response[0]["created_at"],
    )


# ----- Same functionality with '/token' and form data -----
@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), database=Depends(get_db)
):
    user_email = form_data.username
    user_password = form_data.password

    sql_get_user = "app/auth/sql/get_user.sql"

    response = await database.fetch(sql_get_user, user_email)
    if not response:
        # ----- New user flow -----
        hashed_password = get_password_hash(user_password)
        token = create_access_token(
            data={"sub": user_email}, expires_delta=timedelta(minutes=60)
        )
        sql_create_user = "app/auth/sql/create_user.sql"
        response = await database.fetch(
            sql_create_user, user_email, hashed_password, token
        )
    else:
        # ----- Existing user password check -----
        hashed_password = response[0]["hashed_password"]
        if not verify_password(user_password, hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")

        token = response[0]["token"]

    return {"access_token": token, "token_type": "bearer"}
