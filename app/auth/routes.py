import hashlib

from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends, HTTPException

from app.auth.models import (
    UserCreateRequest,
    UserCreateResponse,
    UserGetRequest,
    UserGetResponse,
)
from app.db import get_db

router = APIRouter()


@router.post("/register", response_model=UserCreateResponse)
async def register(user: UserCreateRequest, database=Depends(get_db)):
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()

    sql_path = "app/auth/sql/create_user.sql"

    try:
        response = await database.execute(sql_path, user.email, hashed_password)
    except UniqueViolationError:
        raise HTTPException(status_code=409, detail="User already exists")

    return UserCreateResponse(status=response)


@router.post("/get_user", response_model=UserGetResponse)
async def get_user(user: UserGetRequest, database=Depends(get_db)):
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()

    sql_path = "app/auth/sql/get_user.sql"

    response = await database.fetch(sql_path, user.email, hashed_password)

    if not response:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        response = dict(response[0])

    return UserGetResponse(**response)
