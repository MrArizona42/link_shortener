# app/db.py
import os
from pathlib import Path

import asyncpg

from app.config import settings


class Database:
    def __init__(self):
        self.pool = None
        self.queries = {}
        self.query_timestamps = {}

    async def connect(self):
        """Initialize connection pool."""
        self.pool = await asyncpg.create_pool(settings.DATABASE_URL)

    async def disconnect(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()

    def preload_queries(self):
        """Preload queries into the dictionary."""
        app_dir = Path(__file__).resolve().parent.parent  # goes to the project's root
        for sql_file in app_dir.rglob("*.sql"):
            relative_path = str(sql_file.relative_to(app_dir))
            self.queries[relative_path] = sql_file.read_text()

    async def fetch(self, query_path, *args):
        """Use for SELECT queries."""
        query = self.queries.get(query_path)
        if query is None:
            raise ValueError(f"Query not found for key: {query_path}")

        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def execute(self, query_path, *args):
        """Use for INSERT, UPDATE, DELETE queries."""
        query = self.queries.get(query_path)
        if query is None:
            raise ValueError(f"Query not found for key: {query_path}")

        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)


db = Database()


async def get_db():
    yield db
