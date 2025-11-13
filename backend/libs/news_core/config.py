from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class ServiceSettings(BaseSettings):
    """Shared runtime configuration for every microservice."""

    service_name: str = "dailybrief-service"
    environment: str = Field(default="local", pattern=r"^(local|staging|prod)$")
    log_level: str = "INFO"
    postgres_dsn: str = "postgresql+asyncpg://dailybrief:dailybrief@postgres:5432/dailybrief"
    redis_url: str = "redis://redis:6379/0"
    object_storage_bucket: str = "dailybrief-raw"
    object_storage_region: str = "us-east-1"
    otlp_endpoint: str = "http://otel-collector:4317"
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])
    graphql_depth_limit: int = 15
    jwt_public_key: Optional[str] = None
    admin_emails: List[str] = Field(default_factory=list)

    class Config:
        env_prefix = "DAILYBRIEF_"
        case_sensitive = False


@lru_cache
def get_settings() -> ServiceSettings:
    return ServiceSettings()
