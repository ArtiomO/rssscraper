import re
import typing as tp
from datetime import datetime, timezone

from app.models.exceptions import FieldError
from pydantic import BaseModel, validator

DATE_FORMATS = ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z")
URI_PATTERNS = (
    "^https:\/\/[0-9A-z.]+.[0-9A-z.]+.[A-z]+$",  # noqa: W605
    "^http:\/\/[0-9A-z.]+.[0-9A-z.]+.[A-z]+$",  # noqa: W605
)


def validate_date_formats(v: str, date_formats: tp.Tuple[str, str]) -> datetime:
    """Parse date against formats."""
    for format in date_formats:
        try:
            date = datetime.strptime(v, format)
            if not date.tzinfo:
                date = date.replace(tzinfo=timezone.utc)
            return date
        except ValueError:
            continue

    raise FieldError(field="pub_date", value=v)


class FeedInput(BaseModel):
    uri: str

    @validator("uri", pre=True)
    def parse_uri(cls, v):
        if isinstance(v, str):
            for pattern in URI_PATTERNS:
                result = re.match(pattern, v)
                if result:
                    return v
        raise FieldError(field="uri", value=v)


class Feed(BaseModel):
    id: int
    uri: str
    stalled: bool


class FeedItemInput(BaseModel):
    title: str
    link: str
    summary: str
    published: datetime

    @validator("published", pre=True)
    def parse_published(cls, v):
        if isinstance(v, str):
            v = validate_date_formats(v, date_formats=DATE_FORMATS)
        return v


class FeedItem(BaseModel):
    id: int
    title: str
    link: str
    description: str
    pub_date: datetime
