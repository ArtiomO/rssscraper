import re
import typing as tp
from datetime import datetime, timezone
from pydantic import BaseModel, validator
from app.models.exceptions import FieldError


DATE_FORMATS = ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z")
URI_PATTERNS = (
    r"^https:\/\/[0-9A-z.]+.[0-9A-z.]+.[A-z]+$",  # noqa: W605
    r"^http:\/\/[0-9A-z.]+.[0-9A-z.]+.[A-z]+$",  # noqa: W605
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
    def parse_uri(cls, value):
        if isinstance(value, str):
            for pattern in URI_PATTERNS:
                result = re.match(pattern, value)
                if result:
                    return value
        raise FieldError(field="uri", value=value)


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
    def parse_published(cls, value):
        if isinstance(value, str):
            value = validate_date_formats(value, date_formats=DATE_FORMATS)
        return value


class FeedItem(BaseModel):
    id: int
    title: str
    link: str
    description: str
    pub_date: datetime
