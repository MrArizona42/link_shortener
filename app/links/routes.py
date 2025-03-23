import hashlib
from typing import Annotated

import jwt
import shortuuid
from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.config import settings
from app.db import get_db
from app.links.models import LinkCreateResponse, LinkDeleteResponse, ShortenRequest

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["sub"]


@router.post("/shorten", response_model=LinkCreateResponse)
async def shorten(
    user_email: Annotated[str, Depends(get_current_user)],
    shorten_request: ShortenRequest,
    database=Depends(get_db),
):
    orig_url_str = str(shorten_request.original_url)
    sql_insert_link = "app/links/sql/insert_link.sql"
    for _ in range(2):
        short_code = shortuuid.ShortUUID().random(length=10)
        response = await database.fetch(
            sql_insert_link, orig_url_str, short_code, user_email
        )

        if response:
            break
    else:
        raise HTTPException(
            status_code=409, detail="Failed to generate unique short code"
        )

    short_url = f"{settings.BASE_URL}/{short_code}"

    return LinkCreateResponse(original_url=orig_url_str, short_url=short_url)


@router.get("/{short_code}")
async def redirect(short_code: str, database=Depends(get_db)):
    sql_path = "app/links/sql/get_link_by_short_code.sql"
    response = await database.fetch(sql_path, short_code)
    if not response:
        raise HTTPException(status_code=404, detail="Short URL not found")
    else:
        original_url = response[0]["original_url"]

    return RedirectResponse(url=original_url)


@router.delete("/{short_code}", response_model=LinkDeleteResponse)
async def shorten(
    user_email: Annotated[str, Depends(get_current_user)],
    short_code: str,
    database=Depends(get_db),
):
    sql_delete_link = "app/links/sql/delete_link.sql"
    response = await database.fetch(sql_delete_link, short_code, user_email)
    if not response:
        raise HTTPException(status_code=404, detail="Short URL not found")
    else:
        original_url, short_code = (
            response[0]["original_url"],
            response[0]["short_code"],
        )

    status = f"Deleted {original_url} with short code {short_code}"

    return LinkDeleteResponse(status=status)
