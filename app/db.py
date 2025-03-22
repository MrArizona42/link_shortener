# app/db.py
import asyncpg

from app.config import settings  # Use Pydantic settings


class Database:
    def init(self):
        self.pool = None
        self.queries = {}  # Cache for loaded queries
        self.query_timestamps = {}

    async def connect(self):
        """Initialize connection pool."""
        self.pool = await asyncpg.create_pool(settings.DATABASE_URL)

    async def disconnect(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()

    def load_query(self, module, query_name):
        """Dynamically load SQL query from the configured paths."""
        file_path = settings.SQL_QUERIES[module][query_name]
        last_modified = os.path.getmtime(file_path)

        if (
            query_name not in self.queries
            or self.query_timestamps.get(query_name, 0) < last_modified
        ):
            with open(file_path, "r") as file:
                self.queries[query_name] = file.read()
                self.query_timestamps[query_name] = last_modified

        return self.queries[query_name]

    async def fetch(self, module, query_name, *args):
        """Fetch a single row."""
        query = self.load_query(module, query_name)
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def execute(self, module, query_name, *args):
        """Execute an SQL command."""
        query = self.load_query(module, query_name)
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)


db = Database()


async def get_db():
    return db
