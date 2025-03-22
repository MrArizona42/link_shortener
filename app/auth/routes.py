# app/auth/routes.py
from fastapi import APIRouter, Depends
from app.auth.models import UserCreate, UserResponse
from app.auth.queries import create_user
from app.db import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, database = Depends(get_db)):
    return await create_user(database, user.email, user.password)
