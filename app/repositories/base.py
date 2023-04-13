import abc
import typing as tp
from datetime import datetime

from app.models.feed import Feed
from app.models.user import User


class AbstractFeedRepository(abc.ABC):
    @abc.abstractmethod
    async def save(self, instance, user_id):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_list(self, user_id: int) -> tp.List[Feed]:
        raise NotImplementedError


class AbstractUserRepository(abc.ABC):
    @abc.abstractmethod
    async def save(self, instance):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_list(self) -> tp.List[User]:
        raise NotImplementedError


class AbstractFeedItemRepository(abc.ABC):
    @abc.abstractmethod
    async def save_bulk(self, instances, feed_id):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_latest_date_for_feed_items(self, feed_id: int) -> tp.Optional[datetime]:
        raise NotImplementedError
