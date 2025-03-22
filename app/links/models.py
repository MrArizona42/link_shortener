from datetime import datetime

from pydantic import BaseModel, EmailStr


class LinkCreateRequest(BaseModel):
    email: EmailStr
    password: str
    original_url: str


class LinkCreateResponse(BaseModel):
    status: str
