from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreds(BaseModel):
    email: EmailStr
    password: str


class UserGetResponse(BaseModel):
    id: int
    email: EmailStr
    token: str
    created_at: datetime
