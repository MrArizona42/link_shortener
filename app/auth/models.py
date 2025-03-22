from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreateResponse(BaseModel):
    status: str


class UserGetRequest(BaseModel):
    email: EmailStr
    password: str


class UserGetResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
