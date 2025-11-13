"""Shared domain models, settings, and utilities for DailyBrief backend services."""

from .models import (
    ArticleContent,
    ArticleMetadata,
    ArticleRecord,
    Event,
    EventScore,
    Locale,
    Slate,
    Source,
    SourceAuth,
    SummaryArtifact,
    VerificationResult,
)
from .messages import (
    ArticleFetched,
    ArticleParsed,
    EmbeddingQueued,
    EventCreated,
    EventUpdated,
    SummaryGenerated,
    VerificationCompleted,
)
from .config import ServiceSettings
from .observability import configure_logging, configure_tracer
from .registry import SourceRegistry
from .storage import ObjectStorageClient, PostgresRepository

__all__ = [
    "ArticleContent",
    "ArticleMetadata",
    "ArticleRecord",
    "Event",
    "EventScore",
    "Locale",
    "Slate",
    "Source",
    "SourceAuth",
    "SummaryArtifact",
    "VerificationResult",
    "ArticleFetched",
    "ArticleParsed",
    "EmbeddingQueued",
    "EventCreated",
    "EventUpdated",
    "SummaryGenerated",
    "VerificationCompleted",
    "ServiceSettings",
    "configure_logging",
    "configure_tracer",
    "SourceRegistry",
    "ObjectStorageClient",
    "PostgresRepository",
]
