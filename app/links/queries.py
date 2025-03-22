# app/links/queries.py
from app.links.models import LinkResponse

async def insert_link(database, original_url: str, short_code: str, owner_id: int) -> LinkResponse:
    row = await database.fetch("links", "insert_link", original_url, short_code, owner_id)
    return LinkResponse(id=row["id"], original_url=row["original_url"], short_code=row["short_code"])
