import asyncpg
from app.config import settings
from app.db.exceptions import AlreadyExistsError, NotFoundError

dsn = f"postgres://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"


class Database:
    """Database class to handle connection pool, queries and shutdown."""

    def __init__(self):
        self.connection_pool = None
        self.listener_connection = None

    async def connect(self):
        self.connection_pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=1,
        )

    async def add_listener(self, channel, listener_callback):
        self.listener_connection = await self.connection_pool.acquire()
        await self.listener_connection.add_listener(channel, listener_callback)

    async def remove_listener(self, channel, listener_callback):
        await self.listener_connection.remove_listener(channel, listener_callback)
        await self.connection_pool.release(self.listener_connection)

    async def disconnect(self):
        await self.connection_pool.close()

    async def fetchval(self, query: str, args: tuple = ()):  # type: ignore
        async with self.connection_pool.acquire() as connection:
            async with connection.transaction():
                try:
                    result = await connection.fetchval(query, *args)
                except asyncpg.exceptions.UniqueViolationError as e:
                    raise AlreadyExistsError(detail=e.detail, table_name=e.table_name)
        return result

    async def fetch(self, query: str, args: tuple = ()):  # type: ignore
        async with self.connection_pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetch(query, *args)
        return result

    async def fetchrow(self, query: str, args: tuple = ()):  # type: ignore
        async with self.connection_pool.acquire() as connection:
            async with connection.transaction():
                try:
                    result = await connection.fetchrow(query, *args)
                except asyncpg.exceptions.UniqueViolationError as e:
                    raise AlreadyExistsError(detail=e.detail, table_name=e.table_name)
                if not result:
                    raise NotFoundError

        return result

    async def executemany(self, query: str, args: tuple = ()):  # type: ignore
        async with self.connection_pool.acquire() as connection:
            async with connection.transaction():
                try:
                    result = await connection.executemany(query, args)
                except asyncpg.exceptions.UniqueViolationError as e:
                    raise AlreadyExistsError(detail=e.detail, table_name=e.table_name)
        return result

    async def execute(self, query: str):
        async with self.connection_pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.execute(query)
        return result


db = Database()
