import asyncio
from datetime import datetime, timezone

from news_core import ArticleContent, ArticleMetadata, ServiceSettings, SummaryArtifact

from services.verifier.app.service import VerifierService


def build_article(text: str) -> ArticleContent:
    return ArticleContent(
        metadata=ArticleMetadata(
            id="a",
            source_id="src",
            url="https://example.com",
            title="Title",
            language="en",
            published_at=datetime.now(tz=timezone.utc),
        ),
        text=text,
        raw_html_path="/tmp",
    )


def build_summary(summary: str) -> SummaryArtifact:
    return SummaryArtifact(
        title="", bullets=[], summary=summary, key_quotes=[], sources=[], confidence=0.5, updated_at=datetime.now(tz=timezone.utc)
    )


def test_verifier_flags_low_scores():
    verifier = VerifierService(ServiceSettings(service_name="verifier-test"), threshold=0.5)

    async def _run():
        result = await verifier.verify("evt", build_summary("New cases rose to 10"), [build_article("new cases rose to 10 yesterday")])
        assert result.disputed is False
        result = await verifier.verify("evt", build_summary("Numbers dropped to 5"), [build_article("cases rose to 10")])
        assert result.disputed is True

    asyncio.run(_run())
