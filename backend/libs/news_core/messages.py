from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel

from .models import ArticleMetadata, Event, SummaryArtifact, VerificationResult


class MessageMeta(BaseModel):
    id: str
    timestamp: datetime
    trace_id: str


class ArticleFetched(BaseModel):
    meta: MessageMeta
    article: ArticleMetadata


class ArticleParsed(BaseModel):
    meta: MessageMeta
    article_id: str
    text_hash: str
    tokens: int


class EmbeddingQueued(BaseModel):
    meta: MessageMeta
    article_id: str
    locale: str


class EventCreated(BaseModel):
    meta: MessageMeta
    event: Event


class EventUpdated(BaseModel):
    meta: MessageMeta
    event: Event
    changes: List[str]


class SummaryGenerated(BaseModel):
    meta: MessageMeta
    event_id: str
    artifact: SummaryArtifact


class VerificationCompleted(BaseModel):
    meta: MessageMeta
    result: VerificationResult
