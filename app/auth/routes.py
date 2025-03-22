import hashlib

from fastapi import APIRouter, Depends

from app.auth.models import UserCreate, UserResponse
from app.db import get_db

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, database=Depends(get_db)):
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()

    sql_path = "app/auth/sql/create_user.sql"

    response = await database.execute(sql_path, user.email, hashed_password)

    return UserResponse(status=response)
