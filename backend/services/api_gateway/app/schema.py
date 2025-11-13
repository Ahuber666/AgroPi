from __future__ import annotations

from datetime import datetime
from typing import List

import strawberry

from news_core import Event, Locale, Slate

from .service import GatewayService


def _article_fields(article):
    return {
        "id": article.id,
        "source_id": article.source_id,
        "url": article.url,
        "title": article.title,
        "published_at": article.published_at,
    }


@strawberry.type
class Article:
    id: str
    source_id: str
    url: str
    title: str
    published_at: datetime

    @classmethod
    def from_model(cls, article_model) -> "Article":
        return cls(**_article_fields(article_model))


@strawberry.type
class EventType:
    id: str
    title: str
    topic: str
    articles: List[Article]
    summary: str | None
    confidence: float
    server_score: float

    @classmethod
    def from_model(cls, event: Event) -> "EventType":
        return cls(
            id=event.id,
            title=event.title,
            topic=event.topic,
            articles=[Article.from_model(article) for article in event.articles],
            summary=event.summary,
            confidence=event.confidence,
            server_score=event.server_score,
        )


@strawberry.type
class SlateType:
    id: str
    locale: str
    topic: str
    generated_at: datetime
    events: List[EventType]
    etag: str

    @classmethod
    def from_model(cls, slate: Slate) -> "SlateType":
        return cls(
            id=slate.id,
            locale=slate.locale.value,
            topic=slate.topic,
            generated_at=slate.generated_at,
            events=[EventType.from_model(event) for event in slate.events],
            etag=slate.etag,
        )


class GatewayContext:
    def __init__(self, service: GatewayService):
        self.service = service


@strawberry.type
class Query:
    @strawberry.field
    def slates(self, info, locale: str, topics: List[str]) -> List[SlateType]:
        service: GatewayService = info.context["service"]
        slate_models = service.get_slates(Locale(locale), topics)
        return [SlateType.from_model(slate) for slate in slate_models]


def build_schema(service: GatewayService) -> strawberry.Schema:
    return strawberry.Schema(Query, config=strawberry.SchemaConfig(auto_camel_case=False)), {"service": service}
