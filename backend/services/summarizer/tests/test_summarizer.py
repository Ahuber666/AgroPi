import asyncio
from datetime import datetime, timezone

from news_core import ArticleMetadata, Event, Locale, ServiceSettings

from services.summarizer.app.service import SummarizerService


def build_event() -> Event:
    article = ArticleMetadata(
        id="a",
        source_id="src",
        url="https://example.com/article",
        title="Event Title",
        language="en-US",
        published_at=datetime.now(tz=timezone.utc),
    )
    return Event(
        id="evt",
        title="Event Title",
        topic="World",
        articles=[article],
        summary=None,
        topic_distribution={"world": 1.0},
        locale=Locale.EN_US,
        burst_score=1.0,
        confidence=0.6,
    )


def test_summarize_produces_citation():
    service = SummarizerService(ServiceSettings(service_name="summarizer-test"))

    async def _run():
        event = build_event()
        artifact = await service.summarize(event)
        assert "[1]" in artifact.summary
        assert "UTC" in artifact.summary

    asyncio.run(_run())
