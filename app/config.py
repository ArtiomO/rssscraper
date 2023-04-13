import os
import typing as tp

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Project settings."""

    environment: tp.Optional[str] = os.getenv("ENVIRONMENT")
    log_level: tp.Optional[str] = os.getenv("LOG_LEVEL")
    db_user: tp.Optional[str] = os.getenv("DB_USER")
    db_password: tp.Optional[str] = os.getenv("DB_PASSWORD")
    db_host: tp.Optional[str] = os.getenv("DB_HOST")
    db_port: tp.Optional[str] = os.getenv("DB_PORT")
    db_name: tp.Optional[str] = os.getenv("DB_NAME")
    feeds_sync_interval: tp.Optional[str] = os.getenv("FEEDS_SYNC_INTERVAL")


settings = Settings()
