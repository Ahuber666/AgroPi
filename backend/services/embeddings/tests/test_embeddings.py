import asyncio
from datetime import datetime, timezone

from news_core import ArticleContent, ArticleMetadata, ServiceSettings

from services.embeddings.app.service import EmbeddingsService


def build_article(idx: str, text: str) -> ArticleContent:
    return ArticleContent(
        metadata=ArticleMetadata(
            id=idx,
            source_id="src",
            url="https://example.com",
            title="Title",
            language="en",
            published_at=datetime.now(tz=timezone.utc),
        ),
        text=text,
        raw_html_path="/tmp",
    )


def test_embeddings_deterministic():
    service = EmbeddingsService(ServiceSettings(service_name="embeddings-test"))

    async def _run():
        result1 = await service.embed([build_article("1", "hello world")])
        result2 = await service.embed([build_article("1", "hello world")])
        assert result1[0].vector == result2[0].vector

    asyncio.run(_run())
