from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.db.exceptions import NotFoundError
from app.db.postgres import db
from app.listeners.pg_channel_callback import new_feed_item_callback
from app.models.exceptions import FieldError
from app.repositories.exceptions import FeedAlreadyRegisteredByUser, ItemAlreadyMarkedAsRead
from app.routers import router, wsrouter
from app.services.exceptions import FeedUpdateFailed


def get_app() -> FastAPI:  # noqa C901
    """Init fastapi app."""
    app = FastAPI(
        title="Rssscraper",
        docs_url="/swagger",
        openapi_url="/openapi.json",
        redoc_url=None,
    )

    app.include_router(router)
    app.include_router(wsrouter)

    @app.on_event("startup")
    async def connect_to_db():
        await db.connect()
        await db.add_listener("new_feed_item", new_feed_item_callback)

    @app.on_event("shutdown")
    async def close_db_connecions():
        await db.remove_listener("new_feed_item", new_feed_item_callback)
        await db.disconnect()

    @app.exception_handler(FeedAlreadyRegisteredByUser)
    async def already_registered_handler(exc: FeedAlreadyRegisteredByUser):
        return JSONResponse(
            status_code=400,
            content={"message": exc.message},
        )

    @app.exception_handler(ItemAlreadyMarkedAsRead)
    async def already_marked_as_read_handler(exc: ItemAlreadyMarkedAsRead):
        return JSONResponse(
            status_code=400,
            content={"message": exc.message},
        )

    @app.exception_handler(FeedUpdateFailed)
    async def feed_update_failed_handler(exc: FeedUpdateFailed):
        return JSONResponse(
            status_code=400,
            content={"message": exc.message},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler():
        return JSONResponse(
            status_code=404,
            content={"message": "Not found"},
        )

    @app.exception_handler(FieldError)
    async def field_error_handler(exc: FieldError):
        return JSONResponse(
            status_code=400,
            content={"message": f" Invalid value for field: {exc.field}.  {exc.value}"},
        )

    return app
