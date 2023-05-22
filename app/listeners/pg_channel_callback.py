from app.log import logger_factory
from app.websockets.connections import manager

logger = logger_factory.bind()


async def new_feed_item_callback(connection, pid, channel, payload):
    await manager.broadcast(payload)
    logger.debug("Received notification on channel", channel=channel, payload=payload)
