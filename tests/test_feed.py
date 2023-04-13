from datetime import datetime

import pytest
from app.repositories.feed_repo import feed_update_query
from app.services.exceptions import FeedUpdateFailed


@pytest.mark.parametrize(
    ("id", "uri", "stalled"),
    [(1, "http://test.test", False)],
)
def test_get_feeds(test_client, mock_database, id, uri, stalled):
    """Test get feeds."""
    mock_database([{"id": id, "uri": uri, "stalled": stalled}], "app.repositories.feed_repo.db")
    response = test_client.get("/api/v1.0/feed")
    assert response.status_code == 200
    assert response.json() == [{"id": id, "uri": uri, "stalled": stalled}]


@pytest.mark.parametrize(
    ("id", "uri", "stalled"),
    [(1, "http://test.test", False)],
)
def test_create_feed(test_client, mock_database, id, uri, stalled):
    """Test create feed."""
    mock_database({"id": id, "uri": uri, "stalled": stalled}, "app.repositories.feed_repo.db")
    response = test_client.post("/api/v1.0/feed", json={"uri": uri})
    assert response.status_code == 200
    assert response.json() == {"id": id, "uri": uri, "stalled": stalled}


def test_sync_invalid_feed(test_client, mock_database, mock_exception_http_client):
    """Test invalid feed."""

    mock_exception_http_client("app.services.update_feed.http_client")
    mock_database(
        {"id": 1, "uri": "http://invalid.inv/inv", "stalled": False},
        "app.repositories.feed_repo.db",
    )

    response = test_client.post("/api/v1.0/feed/1/sync")
    assert response.status_code == 400
    assert response.json() == {"message": FeedUpdateFailed.message}


def test_sync_valid_stalled_feed(test_client, mock_database, mock_http_client, rrs_response):
    """Test previously stalled feed updated with stalled = False."""
    mock_http_client(status=200, result=rrs_response, module="app.services.update_feed.http_client")
    feed_db_mock = mock_database(
        {"id": 1, "uri": "http://www.nu.nl/rss/Algemeen", "stalled": True},
        "app.repositories.feed_repo.db",
    )
    date = datetime.strptime("Wed, 05 Apr 2023 10:24:25 +0200", "%a, %d %b %Y %H:%M:%S %z")
    mock_database(
        date,
        "app.repositories.feed_item_repo.db",
    )
    response = test_client.post("/api/v1.0/feed/1/sync")
    assert response.status_code == 200
    called_with = feed_db_mock.fetchrow.call_args.args
    assert called_with[0] == feed_update_query
    assert called_with[1] == (1, False)
