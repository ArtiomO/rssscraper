import typing as tp

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


class UserInput(BaseModel):
    name: str

    def to_db(self) -> tp.Tuple[str]:
        return (self.name,)
