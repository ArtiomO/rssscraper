# Rss scraper

    Rss scraper service.
    Service created as portfolio project so there is no 100% test coverage.
    I am mainly trying to show raw sql usage without orm.

# Environment variables

    DB_HOST=localhost
    DB_NAME=rssscraper
    DB_PASSWORD=root
    DB_PORT=5432
    DB_USER=postgres
    FEEDS_SYNC_INTERVAL=20
    LOG_LEVEL=INFO
    PYTHONUNBUFFERED=1

# Docker

Server listening on port 5000 inside container.

Build:

    docker build -t rss-scraper:0 .
    
# HOW TO

    You can use swagger to communicate with api http://localhost:5000/swagger
    
    First of migrations should be applied to database:

        docker run --rm --init --entrypoint="" --name rss-scraper-migrate --network=host --env-file=.env rss-scraper:0 /src/bin/migrate.sh

    After that launch server container:

        docker run -d --name rss-scraper --network=host --env-file=.env rss-scraper:0    

    Next launch feed updater service:

        docker run --init --entrypoint="" --name rss-scraper-updater --network=host --env-file=.env rss-scraper:0 /src/bin/update_feeds.sh
        
    Now you ready to create user just send POST request to user uri:
        
        POST api/v1.0/user
    
    And use received user id as auth token (That part not really ready for production).

    Now you can create rss feeds:

        POST api/v1.0/feed
        
    Read feed items:
        
        GET api/v1.0/feed/{feed_id}

    Sync feed items manually:
        
        POST api/v1.0/feed/{feed_id}/sync
        
    Get items from all feeds:
        
        GET api/v1.0/item/
    
    Mark item as read:
        
        POST api/v1.0/item/{item-id}/mark-read
    
    
    
    

    

    