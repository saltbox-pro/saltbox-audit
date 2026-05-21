import logging.config
import os
from datetime import timedelta
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from saltbox_sdk.config.mongo_config import MongoSettings
from saltbox_sdk.config.rabbitmq_config import RabbitSettings

CACHE_LIFETIME = timedelta(days=1)
ENV_FILE = Path(os.environ.get('SALTBOX_ENV_FILE', '.env'))


class AppSettings(BaseSettings):
    base_url_root_path: str = '/'
    app_name: str = 'SaltBox Audit Service'
    app_desc: str = 'SaltBox Audit API'
    log_level: str = 'info'
    origins: list[str] = Field(['*'], description='CORS allowed resources')
    basic_auth_username: str = ''
    basic_auth_password: str = ''
    httpx_connect_timeout: float = 5.0
    httpx_read_timeout: float = 5.0
    httpx_write_timeout: float = 5.0
    httpx_pool_timeout: float = 5.0
    httpx_max_connections: int = 100
    httpx_max_keepalive: int = 20
    httpx_keepalive_expiry: float = 5.0

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra='ignore')


class Settings(BaseSettings):
    app: AppSettings = Field(default_factory=AppSettings)
    rabbitmq: RabbitSettings = Field(default_factory=RabbitSettings)
    mongo: MongoSettings = Field(default_factory=MongoSettings)


class LogConfig(BaseModel):
    LOG_FORMAT: str = '%(levelprefix)s [%(filename)s:%(lineno)d] %(message)s'

    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'fmt': LOG_FORMAT,
        },
    }
    handlers: dict = {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stderr',
        },
    }
    loggers: dict = {
        'saltbox_audit': {
            'handlers': ['default'],
            'level': os.environ.get('LOG_LEVEL', 'INFO').upper(),
            'propagate': False,
        },
    }


LOG_CONFIG = LogConfig()

logging.config.dictConfig(LOG_CONFIG.model_dump())

logger = logging.getLogger('saltbox_audit')
