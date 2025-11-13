from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Sequence

from pydantic import BaseModel, Field, HttpUrl


class Locale(str, Enum):
    """Supported locale codes."""

    EN_US = "en-US"
    EN_GB = "en-GB"
    ES_ES = "es-ES"
    FR_FR = "fr-FR"
    AR_AE = "ar-AE"


class SourceAuth(BaseModel):
    """Credential descriptor for a news source."""

    kind: str = Field(description="oauth, api_key, basic, or signed_feed")
    token_env: str = Field(description="Environment variable containing the secret")


class Source(BaseModel):
    id: str
    name: str
    locale: Locale
    priority: int = 0
    rss: Optional[HttpUrl] = None
    json_api: Optional[HttpUrl] = None
    sitemap: Optional[HttpUrl] = None
    partner_feed: Optional[HttpUrl] = None
    robots_txt: Optional[HttpUrl] = None
    auth: Optional[SourceAuth] = None
    reputable: bool = True
    rate_limit_per_min: int = 30


class ArticleMetadata(BaseModel):
    id: str
    source_id: str
    url: HttpUrl
    title: str
    language: str
    published_at: datetime
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    canonical_url: Optional[HttpUrl] = None


class ArticleContent(BaseModel):
    metadata: ArticleMetadata
    text: str
    raw_html_path: str
    summary: Optional[str] = None
    hash: Optional[str] = None


class ArticleRecord(BaseModel):
    content: ArticleContent
    embeddings_id: Optional[str] = None
    duplicate_group: Optional[str] = None


class EventScore(BaseModel):
    recency: float
    sources: float
    diversity: float
    geo: float
    interest: float
    impact: float
    novelty: float
    final: float


class Event(BaseModel):
    id: str
    title: str
    topic: str
    articles: List[ArticleMetadata]
    summary: Optional[str] = None
    topic_distribution: Dict[str, float] = Field(default_factory=dict)
    locale: Locale = Locale.EN_US
    embeddings_key: Optional[str] = None
    taxonomy: List[str] = Field(default_factory=list)
    burst_score: float = 0.0
    disputed: bool = False
    confidence: float = 0.0
    server_score: float = 0.0
    topic_vec: List[float] = Field(default_factory=list)


class SummaryArtifact(BaseModel):
    title: str
    bullets: List[str]
    summary: str
    key_quotes: List[str]
    sources: List[HttpUrl]
    confidence: float
    updated_at: datetime


class VerificationResult(BaseModel):
    event_id: str
    disputed: bool
    confidence: float
    sentence_scores: Dict[int, float]
    numeric_checks: Dict[str, bool]


class Slate(BaseModel):
    id: str
    locale: Locale
    topic: str
    generated_at: datetime
    events: List[Event]
    etag: str


class GraphQLToken(BaseModel):
    user_id: str
    scopes: Sequence[str]
    locale: Locale


class APIRequestContext(BaseModel):
    token: GraphQLToken
    request_id: str
    user_vector: List[float]
