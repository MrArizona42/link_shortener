# app/auth/queries.py
import hashlib
from app.auth.models import UserResponse

async def create_user(database, email: str, password: str) -> UserResponse:
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    row = await database.fetch("auth", "create_user", email, hashed_password)
    return UserResponse(id=row["id"], email=row["email"])
