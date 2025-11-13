from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

from fastapi import HTTPException
from loguru import logger

from news_core import ArticleMetadata, Event, Locale, ServiceSettings, Slate, configure_logging, configure_tracer
from ranking_lib import SlateBuilder


class GatewayService:
    def __init__(self, settings: ServiceSettings):
        self.settings = settings
        self.slate_builder = SlateBuilder()
        self._events = self._seed_events()
        configure_logging(settings.service_name, settings.log_level)
        configure_tracer(settings)

    def _seed_events(self) -> Dict[str, List[Event]]:
        events: Dict[str, List[Event]] = {}
        now = datetime.now(tz=timezone.utc)
        sample_articles: List[ArticleMetadata] = [
            ArticleMetadata(
                id="nyt-1",
                source_id="nyt_rss",
                url="https://example.com/story",
                title="Leaders meet for summit",
                language="en-US",
                published_at=now - timedelta(hours=1),
            )
        ]
        events[Locale.EN_US.value] = [
            Event(
                id="evt-1",
                title="Leaders meet for summit",
                topic="world",
                articles=sample_articles,
                summary=None,
                topic_distribution={"world": 1.0},
                locale=Locale.EN_US,
                taxonomy=["World"],
                burst_score=1.3,
                confidence=0.8,
                server_score=0.8,
                topic_vec=[0.1, 0.9],
            )
        ]
        return events

    def get_slates(self, locale: Locale, topics: List[str]) -> List[Slate]:
        events = self._events.get(locale.value, [])
        slates: List[Slate] = []
        for topic in topics:
            topic_events = [event for event in events if event.topic == topic]
            if not topic_events:
                raise HTTPException(status_code=404, detail=f"No events for topic {topic}")
            slates.append(self.slate_builder.build(topic_events, locale=locale, topic=topic))
        return slates

    def get_source_logo(self, source_id: str) -> Path:
        root = Path(__file__).resolve().parents[3]
        path = root / "static" / "source_logos" / f"{source_id}.svg"
        if not path.exists():
            raise HTTPException(status_code=404, detail="Logo not found")
        logger.info("serving_logo", source_id=source_id, path=str(path))
        return path
