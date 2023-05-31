import typing as tp
from functools import wraps
from time import sleep

from app.log import logger_factory

FUNC_RESULT = tp.TypeVar("FUNC_RESULT")

logger = logger_factory.bind()


def retry(  # noqa C901
    *exceptions: tp.Type[Exception],
    attempts: int = 3,
    wait_time_seconds: float = 0.5,
    backoff: int = 2,
) -> tp.Callable[[tp.Callable], tp.Callable]:  # type: ignore
    """Try to call a func `attempts` times with `wait_time_seconds`
    breaks multiplied each time by `backoff` raise catched exception."""

    def _retry(func: tp.Callable) -> tp.Callable:  # type: ignore
        @wraps(func)
        async def _inner(*args, **kwargs: dict) -> FUNC_RESULT:
            exception: Exception = Exception()
            wait = wait_time_seconds
            for attempt in range(attempts):
                try:
                    res: FUNC_RESULT = await func(*args, **kwargs)
                    if attempt >= 1:
                        logger.warning(message="Successfully retrieved rss", attempts=attempt)
                except exceptions as exc:
                    exception = exc
                    sleep(wait)
                    wait *= backoff
                    continue
                break
            else:
                raise exception
            return res

        return tp.cast(tp.Callable, _inner)  # type: ignore

    return _retry
