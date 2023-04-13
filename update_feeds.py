import asyncio

from app.clients.http import HttpClientConnectionError
from app.config import settings
from app.db.postgres import db
from app.repositories.feed_repo import feed_repo
from app.services.update_feed import sync_feed_items


async def sync_feeds():
    """Sync all feeds."""

    while True:
        feeds = await feed_repo.get_list_active()
        for feed in feeds:
            try:
                await sync_feed_items(feed.uri, feed.id)
            except HttpClientConnectionError:
                await feed_repo.update(feed.id, stalled=True)

        await asyncio.sleep(int(settings.feeds_sync_interval))


async def execute_command():
    """Main command execution function."""
    await db.connect()
    await sync_feeds()
    await db.disconnect()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(execute_command())
    except (KeyboardInterrupt, SystemExit):
        loop.run_until_complete(db.disconnect())
        pass
