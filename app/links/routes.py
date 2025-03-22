import hashlib

import shortuuid
from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, Depends, HTTPException

from app.config import settings
from app.db import get_db
from app.links.models import LinkCreateRequest, LinkCreateResponse

router = APIRouter()


@router.post("/shorten", response_model=LinkCreateResponse)
async def register(link: LinkCreateRequest, database=Depends(get_db)):
    hashed_password = hashlib.sha256(link.password.encode()).hexdigest()

    # -----Check user -------
    sql_path = "app/links/sql/get_owner_id.sql"
    response = await database.fetch(sql_path, link.email, hashed_password)
    if not response:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        owner_id = response[0]["id"]

    # -----Shorten link -------
    sql_path = "app/links/sql/insert_link.sql"
    max_retry = 5
    for _ in range(max_retry):
        try:
            short_code = shortuuid.ShortUUID().random(length=10)
            await database.execute(sql_path, link.original_url, short_code, owner_id)
            break
        except UniqueViolationError:
            pass
    else:
        raise HTTPException(
            status_code=409, detail="Failed to generate unique short code"
        )

    short_code = shortuuid.ShortUUID().random(length=10)
    short_url = f"Shortened URL: {settings.BASE_URL}/{short_code}"
    status = f"{link.original_url} shortened to {short_url}"

    return LinkCreateResponse(status=status)
