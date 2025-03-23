from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl


class LinkCreateResponse(BaseModel):
    original_url: HttpUrl
    short_url: HttpUrl


class LinkDeleteResponse(BaseModel):
    status: str


class ShortenRequest(BaseModel):
    original_url: HttpUrl
    short_code: Optional[str] = None
    expiration_period: Optional[int] = None


class UpdateURLRequest(BaseModel):
    new_original_url: HttpUrl
