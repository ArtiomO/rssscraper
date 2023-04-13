import pytest
from app.db.exceptions import NotFoundError
from app.models.exceptions import FieldError
from app.repositories.exceptions import FeedAlreadyRegisteredByUser, ItemAlreadyMarkedAsRead
from app.routers import router
from app.services.exceptions import FeedUpdateFailed
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient


def get_app() -> FastAPI:
    """Init fastapi app."""
    app = FastAPI(
        title="TestApp",
        docs_url="/swagger",
        openapi_url="/openapi.json",
        redoc_url=None,
    )

    app.include_router(router)

    @app.exception_handler(FeedAlreadyRegisteredByUser)
    async def already_registered_handler(request: Request, exc: FeedAlreadyRegisteredByUser):
        return JSONResponse(
            status_code=400,
            content={"message": exc.message},
        )

    @app.exception_handler(ItemAlreadyMarkedAsRead)
    async def already_marked_as_read_handler(request: Request, exc: ItemAlreadyMarkedAsRead):
        return JSONResponse(
            status_code=400,
            content={"message": exc.message},
        )

    @app.exception_handler(FeedUpdateFailed)
    async def feed_update_failed_handler(request: Request, exc: FeedUpdateFailed):
        return JSONResponse(
            status_code=400,
            content={"message": exc.message},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={"message": "Not found"},
        )

    @app.exception_handler(FieldError)
    async def field_error_handler(request: Request, exc: FieldError):
        return JSONResponse(
            status_code=400,
            content={"message": f" Invalid value for field: {exc.field}.  {exc.value}"},
        )

    return app


@pytest.fixture()
def test_client():
    client = TestClient(app=get_app())
    client.headers = {"Authorization": "Bearer 2"}

    return client
