from fastapi import FastAPI, Request

from app.config import settings
from app.db import db  # our Database instance

app = FastAPI(title="ShortLinks App")


@app.on_event("startup")
async def startup():
    await db.connect()  # Initializes the connection pool
    db.preload_queries()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()  # Closes the connection pool


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


# Include the auth routes (similar setup can be done for links)
# app.include_router(auth_router, prefix="/auth", tags=["auth"])
