import asyncio

from app.db.postgres import db
from app.migrations.initial_migration import initial_migration_script
from asyncpg.exceptions import DuplicateTableError


async def execute_migrations() -> None:
    await db.connect()  # type: ignore
    try:
        await db.execute(initial_migration_script)
    except DuplicateTableError:
        pass
    await db.disconnect()  # type: ignore


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(execute_migrations())
