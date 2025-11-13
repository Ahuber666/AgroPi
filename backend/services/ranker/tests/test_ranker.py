from datetime import datetime, timezone

from news_core import ArticleMetadata, Event, Locale, ServiceSettings

from services.ranker.app.service import RankerService


def build_event(event_id: str, score: float) -> Event:
    metadata = ArticleMetadata(
        id=f"art-{event_id}",
        source_id="src",
        url="https://example.com",
        title="Title",
        language="en-US",
        published_at=datetime.now(tz=timezone.utc),
    )
    return Event(
        id=event_id,
        title=f"Event {event_id}",
        topic="world",
        articles=[metadata],
        summary=None,
        topic_distribution={"world": 1.0},
        locale=Locale.EN_US,
        burst_score=1.0,
        confidence=score,
        server_score=score,
    )


def test_ranker_builds_slates():
    service = RankerService(ServiceSettings(service_name="ranker-test"))
    events = [build_event("1", 0.9), build_event("2", 0.3)]
    result = service.build_slates(events, [Locale.EN_US])
    assert "en-US" in result
    assert result["en-US"][0].events[0].id in {"1", "2"}
