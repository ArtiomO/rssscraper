from datetime import datetime


def test_get_feed_items(test_client, mock_database):
    date = datetime.now()
    feed_id = 1

    instance = {
        "id": 1,
        "title": "Test title",
        "link": "http://test.test.com",
        "description": "test",
        "pub_date": date,
    }

    resp_json = {
        "id": feed_id,
        "title": "Test title",
        "link": "http://test.test.com",
        "description": "test",
        "pub_date": date.strftime("%Y-%m-%dT%H:%M:%S.%f"),
    }

    mock_database([instance], "app.repositories.feed_item_repo.db")

    response = test_client.get(f"/api/v1.0/feed/{feed_id}")
    assert response.status_code == 200
    assert response.json() == [resp_json]


def test_get_all_items(test_client, mock_database):
    date = datetime.now()

    instances = [
        {
            "id": 1,
            "title": "Test title",
            "link": "http://test.test.com",
            "description": "test",
            "pub_date": date,
        },
        {
            "id": 2,
            "title": "Test title2",
            "link": "http://test.test2.com",
            "description": "test2",
            "pub_date": date,
        },
    ]

    resp_json = [
        {
            "id": 1,
            "title": "Test title",
            "link": "http://test.test.com",
            "description": "test",
            "pub_date": date.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        },
        {
            "id": 2,
            "title": "Test title2",
            "link": "http://test.test2.com",
            "description": "test2",
            "pub_date": date.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        },
    ]

    mock_database(instances, "app.repositories.feed_item_repo.db")

    response = test_client.get("/api/v1.0/item/")
    assert response.status_code == 200
    assert response.json() == resp_json
