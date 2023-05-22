import typing as tp
from datetime import datetime

import feedparser
from app.clients.http import http_client
from app.models.feed import FeedItemInput

from bs4 import BeautifulSoup
import html

from app.repositories.feed_item_repo import FeedItemRepository


def parse_feed(resp_body: str) -> feedparser.FeedParserDict:
    """Feedparser library wrapper."""

    return feedparser.parse(resp_body)


def deserialize_parsed(parsed: feedparser.FeedParserDict) -> tp.List[FeedItemInput]:
    """Create list of Feed item instances."""

    feed_items = []

    for item in parsed.entries:
        parsed_item = FeedItemInput.parse_obj(dict(item))
        soup_summary = BeautifulSoup(html.unescape(parsed_item.summary), "html.parser")
        soup_title = BeautifulSoup(html.unescape(parsed_item.title), "html.parser")

        parsed_item.summary = soup_summary.text
        parsed_item.title = soup_title.text

        feed_items.append(parsed_item)

    return feed_items


def get_newest_items(in_list: tp.List[FeedItemInput], date: datetime) -> tp.List[FeedItemInput]:
    """Get feeds published after provided date."""

    return list(filter(lambda item: (item.published > date), in_list))


async def sync_feed_items(feed_item_repo: FeedItemRepository, feed_uri: str, feed_id: int):
    """Sync feed items main function."""

    _, response = await http_client.request(method="get", url=feed_uri)
    parsed_feed = parse_feed(response)
    items = deserialize_parsed(parsed_feed)
    latest_item_date = await feed_item_repo.get_latest_date_for_feed_items(feed_id)
    if latest_item_date:
        items = get_newest_items(items, latest_item_date)

    await feed_item_repo.save_bulk(items, feed_id)
