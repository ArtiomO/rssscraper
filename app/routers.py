import typing as tp
from typing import Annotated

from app.clients.http import HttpClientConnectionError
from app.models.feed import Feed, FeedInput, FeedItem
from app.models.user import User, UserInput
from app.repositories.feed_item_repo import FeedItemPostgreRepository, FeedItemRepository
from app.repositories.feed_repo import FeedPostgreRepository, FeedRepository
from app.repositories.user_repo import UserPostgreRepository, UserRepository
from app.services.exceptions import FeedUpdateFailed
from app.services.update_feed import sync_feed_items
from app.websockets.connections import manager
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer

router = APIRouter(
    prefix="/api",
)

wsrouter = APIRouter(
    prefix="/ws",
)

auth_scheme = HTTPBearer()


@router.post("/v1.0/user")
async def user_create(
    user_repo: Annotated[UserRepository, Depends(UserPostgreRepository)], user_in: UserInput
) -> User:
    """Register user."""
    return await user_repo.save(user_in)


@router.post("/v1.0/feed")
async def feed_create(
    feed_repo: Annotated[FeedRepository, Depends(FeedPostgreRepository)],
    feed_in: FeedInput,
    user: HTTPBearer = Depends(auth_scheme),
) -> Feed:
    """Register feed."""
    return await feed_repo.save(feed_in, int(user.credentials))


@router.get("/v1.0/feed")
async def feed_list(
    feed_repo: Annotated[FeedRepository, Depends(FeedPostgreRepository)],
    user: HTTPBearer = Depends(auth_scheme),
) -> tp.List[Feed]:
    """Get feeds."""
    return await feed_repo.get_list(int(user.credentials))


@router.get("/v1.0/feed/{feed_id}")
async def feed_items(
    feed_item_repo: Annotated[FeedItemRepository, Depends(FeedItemPostgreRepository)],
    feed_id: int,
    read: bool = False,
    order_by_date_asc: bool = False,
    user: HTTPBearer = Depends(auth_scheme),
) -> tp.List[FeedItem]:
    """Get feed items."""
    return await feed_item_repo.get_feed_all_items(
        int(user.credentials), feed_id, read, order_by_date_asc
    )


@router.post("/v1.0/feed/{feed_id}/sync")
async def sync_feed(
    feed_repo: Annotated[FeedRepository, Depends(FeedPostgreRepository)],
    feed_item_repo: Annotated[FeedItemRepository, Depends(FeedItemPostgreRepository)],
    feed_id: int,
    user: HTTPBearer = Depends(auth_scheme),
):
    """Sync feed items."""

    feed = await feed_repo.get_for_user(int(user.credentials), feed_id)

    try:
        await sync_feed_items(feed_item_repo, feed.uri, feed.id)
        await feed_repo.update(feed.id, stalled=False)
    except HttpClientConnectionError:
        await feed_repo.update(feed.id, stalled=True)
        raise FeedUpdateFailed

    return 200


@router.get("/v1.0/item/")
async def get_all_items(
    feed_item_repo: Annotated[FeedItemRepository, Depends(FeedItemPostgreRepository)],
    read: bool = False,
    orderByDateAsc: bool = False,
    user: HTTPBearer = Depends(auth_scheme),
) -> tp.List[FeedItem]:
    """Get all items from all feeds."""
    return await feed_item_repo.get_all_items(int(user.credentials), read, orderByDateAsc)


@router.post("/v1.0/item/{item_id}/mark-read")
async def mark_read(
    feed_item_repo: Annotated[FeedItemRepository, Depends(FeedItemPostgreRepository)],
    item_id: int,
    user: HTTPBearer = Depends(auth_scheme),
):
    """Get feed items."""
    return await feed_item_repo.feed_item_mark_read(int(user.credentials), item_id)


@wsrouter.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
