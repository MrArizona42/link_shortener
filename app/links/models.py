from datetime import datetime

from pydantic import BaseModel, EmailStr, HttpUrl


class LinkCreateResponse(BaseModel):
    original_url: HttpUrl
    short_url: HttpUrl


class LinkDeleteResponse(BaseModel):
    status: str


class ShortenRequest(BaseModel):
    original_url: HttpUrl
