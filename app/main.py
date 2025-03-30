from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.auth.routes import router as auth_router
from app.config import settings
from app.db import db  # our Database instance
from app.links.routes import router as links_router
from app.redis_client import close_redis, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    db.preload_queries()
    await init_redis()
    try:
        yield
    finally:
        await db.disconnect()
        await close_redis()


app = FastAPI(title="ShortLinks App", lifespan=lifespan)


@app.get("/")
async def root(request: Request):
    client_host = request.client.host

    connection_check_sql = "app/sql/check_connection.sql"
    today = await db.fetch(connection_check_sql)

    message = (
        f"Hello from FastAPI running on {settings.APP_HOST}:{settings.APP_PORT}. "
        f"Postgres URL: {settings.DATABASE_URL}. "
        f"DB queries: {list(db.queries.keys())}. "
        f"Your IP: {client_host}"
        f"PostgreSQL connection is healthy! Today's date: {today}"
    )
    return {"message": message}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(links_router, prefix="/links", tags=["links"])
