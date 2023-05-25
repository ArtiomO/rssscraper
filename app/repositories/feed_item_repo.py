import typing as tp
from datetime import datetime

from app.db import exceptions
from app.db.postgres import db
from app.models.feed import FeedItem, FeedItemInput
from app.repositories.exceptions import ItemAlreadyMarkedAsRead
from pypika import Order, Query, Tables

feed_item_save_query = """
INSERT INTO feed_item (title, link, description, pub_date, feed_id)
VALUES ($1, $2, $3, $4, $5);
"""

feed_item_latest_date = """
SELECT pub_date
FROM feed_item
         INNER JOIN feed f ON f.id = feed_item.feed_id
WHERE f.id = $1
ORDER BY feed_item.pub_date DESC
LIMIT 1;
"""

registered_feeds, feed, feed_item, read_item = Tables(
    "registered_feeds", "feed", "feed_item", "read_item"
)


feed_items_base_query = Query.from_("feed_item").select(
    "id", "title", "link", "description", "pub_date", "feed_id"
)

all_items_base_query = (
    Query.from_("feed_item")
    .select("id", "title", "link", "description", "pub_date", "feed_id")
    .inner_join(registered_feeds)
    .on(feed_item.feed_id == registered_feeds.feed_id)
)

read_items_subquery = (
    Query.from_("feed_item")
    .select(
        "id",
    )
    .inner_join(read_item)
    .on(feed_item.id == read_item.item_id)
)


feed_items_unread_query = """
SELECT feed_item.id as id, title, link, description, pub_date
from feed_item
         left join read_item ri on feed_item.id = ri.item_id
where feed_item.feed_id = $1 and ri.user_id is null or ri.user_id != $2
order by pub_date desc;
"""

feed_item_mark_read = """
INSERT INTO read_item (user_id, item_id)
VALUES ($1, $2);
"""

registration_save_query = """
INSERT INTO registered_feeds (user_id, feed_id)
VALUES ($1, $2)
RETURNING (user_id, feed_id);
"""


def feed_input_to_db(instances: tp.List[FeedItemInput], feed_id: int) -> tp.List[tp.Tuple]:  # type: ignore
    """Convert feeds input to db ready tuples."""
    result = []
    for instance in instances:
        values = []
        for _, value in instance:
            values.append(value)
        values.append(feed_id)
        result.append(tuple(values))

    return result


class FeedItemRepository(tp.Protocol):
    """feed item repository."""

    async def save_bulk(self, instances: tp.List[FeedItemInput], feed_id: int):
        """Save items bulk."""


    async def get_latest_date_for_feed_items(self, feed_id: int) -> tp.Optional[datetime]:
        """Get latest pub date for feed id."""

    async def get_feed_all_items(
        self, user_id, feed_id: int, read: bool, order_by_date_asc: bool
    ) -> tp.List[FeedItem]:
        """Get feed read items."""

        ...

    async def get_all_items(
        self, user_id: int, read: bool, order_by_date_asc: bool
    ) -> tp.List[FeedItem]:
        """Get all items."""

        ...

    async def get_feed_items_unread(self, feed_id: int, user_id: int) -> tp.List[FeedItem]:
        """Get feed unread items."""
        ...

    async def feed_item_mark_read(self, user_id: int, item_id: int):
        """Mark item as read."""
        ...


class FeedItemPostgreRepository:
    """feed item repository."""

    async def save_bulk(self, instances: tp.List[FeedItemInput], feed_id: int):
        """Save items bulk."""
        instances_for_db = feed_input_to_db(instances, feed_id)
        await db.executemany(feed_item_save_query, instances_for_db)

    async def get_latest_date_for_feed_items(self, feed_id: int) -> tp.Optional[datetime]:
        """Get latest pub date for feed id."""
        latest_date = await db.fetchval(feed_item_latest_date, (feed_id,))

        if not latest_date:
            return None

        return latest_date

    async def get_feed_all_items(
        self, user_id, feed_id: int, read: bool, order_by_date_asc: bool
    ) -> tp.List[FeedItem]:
        """Get feed read items."""

        query = feed_items_base_query.where(feed_item.feed_id == feed_id)

        if not read:
            subquery = read_items_subquery.where(read_item.user_id == user_id)
            query = query.where(feed_item.id.notin(subquery))

        if order_by_date_asc:
            query = query.orderby("pub_date", order=Order.asc)
        else:
            query = query.orderby("pub_date", order=Order.desc)

        items = await db.fetch(str(query), ())

        return [FeedItem.parse_obj(dict(row)) for row in items]

    async def get_all_items(
        self, user_id: int, read: bool, order_by_date_asc: bool
    ) -> tp.List[FeedItem]:
        """Get all items."""

        query = all_items_base_query.where(registered_feeds.user_id == user_id)

        if not read:
            subquery = read_items_subquery.where(read_item.user_id == user_id)
            query = query.where(feed_item.id.notin(subquery))

        if order_by_date_asc:
            query = query.orderby("pub_date", order=Order.asc)
        else:
            query = query.orderby("pub_date", order=Order.desc)

        items = await db.fetch(str(query), ())

        return [FeedItem.parse_obj(dict(row)) for row in items]

    async def get_feed_items_unread(self, feed_id: int, user_id: int) -> tp.List[FeedItem]:
        """Get feed unread items."""
        items = await db.fetch(feed_items_unread_query, (feed_id, user_id))

        return [FeedItem.parse_obj(dict(row)) for row in items]

    async def feed_item_mark_read(self, user_id: int, item_id: int):
        """Mark item as read."""
        try:
            await db.fetchrow(feed_item_mark_read, (user_id, item_id))
        except exceptions.AlreadyExistsError:
            raise ItemAlreadyMarkedAsRead
