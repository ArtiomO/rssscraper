import typing as tp

from app.db.postgres import db
from app.models.user import User, UserInput

user_save_query = """
INSERT INTO "user" (name)
VALUES ($1)
RETURNING (id, name, created_at);
"""

user_query = """
SELECT * FROM "user";
"""


class UserRepository(tp.Protocol):
    async def save(self, instance: UserInput) -> User:
        ...

    async def get_list(self) -> tp.List[User]:
        ...


class UserPostgreRepository:
    """User repository."""

    async def save(self, instance: UserInput) -> User:
        saved_instance = await db.fetchval(user_save_query, (instance.to_db()))
        return User.parse_obj({"id": saved_instance[0], "name": saved_instance[1]})

    async def get_list(self) -> tp.List[User]:
        result = await db.fetch(user_query)
        return [User.parse_obj(dict(row)) for row in result]
