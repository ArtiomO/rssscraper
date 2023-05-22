import typing as tp

from app.db import exceptions
from app.db.postgres import db
from app.models.feed import Feed, FeedInput
from app.repositories.exceptions import FeedAlreadyRegisteredByUser

feed_save_query = """
INSERT INTO feed (uri)
VALUES ($1)
RETURNING *;
"""

feed_update_query = """
UPDATE feed
SET stalled = $2
WHERE id = $1
RETURNING *;
"""

feed_get_query = """
SELECT * FROM feed
WHERE uri = $1
"""

registration_save_query = """
INSERT INTO registered_feeds (user_id, feed_id)
VALUES ($1, $2)
RETURNING (user_id, feed_id);
"""

feed_query = """
SELECT feed.id, feed.uri, feed.stalled
FROM feed
         INNER JOIN registered_feeds rf ON feed.id = rf.feed_id
         INNER JOIN "user" u ON u.id = rf.user_id
WHERE u.id = $1;
"""

feed_query_active = """
SELECT *
FROM feed
where stalled = FALSE;
"""

feed_query_by_id = """
SELECT *
FROM feed
WHERE id = $1;
"""

feed_query_by_user = """
SELECT * from feed
    inner join registered_feeds rf on feed.id = rf.feed_id
where rf.user_id = $1 and feed.id = $2;
"""


class FeedRepository(tp.Protocol):
    async def save(self, instance: FeedInput, registered_by: str) -> Feed:
        ...

    async def get_list(self, user_id: int) -> tp.List[Feed]:
        ...

    async def update(self, feed_id: int, stalled: bool) -> Feed:
        ...

    async def get_list_active(self) -> tp.List[Feed]:
        ...

    async def get(self, feed_id: int) -> Feed:
        ...

    async def get_for_user(self, user_id: int, feed_id: int) -> Feed:
        ...


class FeedPostgreRepository:
    """Feed repository."""

    async def save(self, instance: FeedInput, registered_by: str) -> Feed:
        try:
            feed = await db.fetchrow(feed_save_query, (instance.uri,))
        except exceptions.AlreadyExistsError:
            feed = await db.fetchrow(feed_get_query, (instance.uri,))
        feed = Feed.parse_obj(dict(feed))
        try:
            await db.fetchval(registration_save_query, (int(registered_by), feed.id))
        except exceptions.AlreadyExistsError:
            raise FeedAlreadyRegisteredByUser
        return feed

    async def get_list(self, user_id: int) -> tp.List[Feed]:
        result = await db.fetch(feed_query, (user_id,))
        return [Feed.parse_obj(dict(row)) for row in result]

    async def update(self, feed_id: int, stalled: bool) -> Feed:
        result = await db.fetchrow(feed_update_query, (feed_id, stalled))
        return Feed.parse_obj(dict(result))

    async def get_list_active(self) -> tp.List[Feed]:
        result = await db.fetch(feed_query_active)
        return [Feed.parse_obj(dict(row)) for row in result]

    async def get(self, feed_id: int) -> Feed:
        result = await db.fetchrow(feed_query_by_id, (feed_id,))
        return Feed.parse_obj(dict(result))

    async def get_for_user(self, user_id: int, feed_id: int) -> Feed:
        result = await db.fetchrow(feed_query_by_user, (user_id, feed_id))
        return Feed.parse_obj(dict(result))
