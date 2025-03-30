import json
import time
from typing import Annotated

import jwt
import shortuuid
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.db import get_db
from app.links.models import (
    GetStatsResponse,
    LinkCreateResponse,
    LinkDeleteResponse,
    ShortenRequest,
    UpdateURLRequest,
)
from app.redis_client import get_redis

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
    if shorten_request.short_code:
        short_code = shorten_request.short_code
        response = await database.fetch(
            sql_insert_link,
            orig_url_str,
            short_code,
            user_email,
            shorten_request.expires_at,
        )
        if not response:
            raise HTTPException(
                status_code=409, detail="Failed to insert custom code, it's not unique"
            )
    else:
        for _ in range(2):
            short_code = shortuuid.ShortUUID().random(length=10)
            response = await database.fetch(
                sql_insert_link,
                orig_url_str,
                short_code,
                user_email,
                shorten_request.expires_at,
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
async def redirect(short_code: str, request: Request, database=Depends(get_db)):
    sql_path = "app/links/sql/get_link_by_short_code.sql"
    response = await database.fetch(sql_path, short_code)
    if not response:
        raise HTTPException(status_code=404, detail="Short URL not found")
    else:
        original_url = response[0]["original_url"]

    log_sql_path = "app/links/sql/log_redirect.sql"
    user_agent = request.headers.get("User-Agent", "Unknown")
    ip_address = request.client.host

    await database.execute(log_sql_path, short_code, user_agent, ip_address)

    return RedirectResponse(url=original_url)


@router.delete("/{short_code}", response_model=LinkDeleteResponse)
async def delete_short_code(
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


@router.put("/{short_code}")
async def update_orig_url(
    user_email: Annotated[str, Depends(get_current_user)],
    short_code: str,
    update_url_request: UpdateURLRequest,
    database=Depends(get_db),
):
    new_url_str = str(update_url_request.new_original_url)
    sql_update_link = "app/links/sql/update_link_by_short_code.sql"
    response = await database.fetch(
        sql_update_link, new_url_str, short_code, user_email
    )
    if not response:
        raise HTTPException(status_code=404, detail="Short URL not found")
    else:
        original_url, short_code = (
            response[0]["original_url"],
            response[0]["short_code"],
        )

    short_url = f"{settings.BASE_URL}/{short_code}"

    return LinkCreateResponse(original_url=original_url, short_url=short_url)


@router.get("/{short_code}/stats", response_model=GetStatsResponse)
async def get_redirect_stats(
    user_email: Annotated[str, Depends(get_current_user)],
    short_code: str,
    database=Depends(get_db),
    redis=Depends(get_redis),
):
    cache_key = f"item:{user_email}:{short_code}"

    cached_data = await redis.get(cache_key)
    if cached_data:
        cached_response = json.loads(cached_data)
        return GetStatsResponse(
            short_code=short_code,
            total_redirects=cached_response["total_redirects"],
        )

    time.sleep(5)
    sql_path = "app/links/sql/get_redirect_count.sql"
    response = await database.fetch(sql_path, short_code, user_email)

    if len(response) == 0:
        raise HTTPException(status_code=404, detail="No stats for this link")
    else:
        redirect_count = response[0]["total_redirects"]
        await redis.setex(
            cache_key,
            settings.REDIS_CACHE_EXPIRE,
            json.dumps({"total_redirects": redirect_count}),
        )
        time.sleep(5)

    return GetStatsResponse(short_code=short_code, total_redirects=int(redirect_count))
