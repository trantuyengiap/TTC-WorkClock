from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import EmailStr, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / '.env'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding='utf-8',
        extra='ignore',
    )

    app_name: str = 'TTC WorkClock Admin'
    app_env: str = 'development'
    app_secret_key: str = 'change-me'
    app_access_token_expire_minutes: int = 720
    app_timezone: str = 'Asia/Ho_Chi_Minh'
    api_v1_prefix: str = '/api/v1'
    backend_cors_origins: List[str] = Field(default_factory=lambda: ['http://localhost:5173'])

    database_url: str = 'postgresql+psycopg://workclock:workclock@localhost:5432/workclock'
    redis_url: str = 'redis://localhost:6379/0'
    celery_broker_url: str = 'redis://localhost:6379/1'
    celery_result_backend: str = 'redis://localhost:6379/2'

    elasticsearch_url: str = 'http://localhost:9200'
    elasticsearch_username: str | None = None
    elasticsearch_password: str | None = None
    elasticsearch_index_pattern: str = 'hikvision-*'
    elasticsearch_verify_certs: bool = False
    elasticsearch_request_timeout: int = 30

    es_field_timestamp: str = '@timestamp'
    es_field_event_time: str = 'hikvision.dateTime'
    es_field_user_id: str = 'hikvision.AccessControllerEvent.employeeNoString'
    es_field_user_name: str = 'hikvision.AccessControllerEvent.name'
    es_field_device_name: str = 'hikvision.AccessControllerEvent.deviceName'
    es_field_device_id: str = 'hikvision.deviceID'

    smtp_host: str = 'localhost'
    smtp_port: int = 1025
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: EmailStr = 'info@ttcdanghuynh.vn'

    viber_base_url: str = 'http://localhost:8080'
    viber_send_endpoint: str = '/viber/send'
    viber_token: str | None = None

    default_admin_username: str = 'admin'
    default_admin_password: str = 'Admin@123'
    default_admin_email: EmailStr = 'info@ttcdanghuynh.vn'

    @field_validator('backend_cors_origins', mode='before')
    @classmethod
    def assemble_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()