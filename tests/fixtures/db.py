import typing as tp
from unittest.mock import AsyncMock

import pytest


class FakeDatabase:
    """Fake database for db queries mocking."""

    def __init__(self, results: tp.List[dict]):
        self._results = results

    async def fetchval(self, query: str, args: tuple = ()):
        return self._results

    async def fetch(self, query: str, args: tuple = ()):
        return self._results

    async def fetchrow(self, query: str, args: tuple = ()):
        return self._results

    async def executemany(self, query: str, args: tuple = ()):
        return self._results

    async def execute(self, query: str):
        return self._results


@pytest.fixture()
def mock_database(mocker):
    """Mock template model repo."""

    def factory(result: tp.List[dict], module: str):
        db_instance = FakeDatabase(result)
        db_instance.fetchrow = AsyncMock(return_value=result)
        return mocker.patch(module, db_instance)

    return factory
