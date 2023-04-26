from app.log import logger_factory
from app.websockets.connections import manager
import json

logger = logger_factory.bind()
async def new_feed_item_callback(connection, pid, channel, payload):

    await manager.broadcast(payload)
    logger.debug("Received notification on channel", channel=channel, payload=payload)

