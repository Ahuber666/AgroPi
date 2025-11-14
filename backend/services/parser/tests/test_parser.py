import asyncio
from datetime import datetime, timezone

from news_core import ArticleMetadata, ServiceSettings

from services.parser.app.service import ParserService


def test_normalize_strips_scripts():
    parser = ParserService(ServiceSettings(service_name="parser-test"))
    html = """
    <html><body>
    <script>console.log('x')</script>
    <p>Headline</p>
    </body></html>
    """
    cleaned = parser.normalize_html(html)
    assert "console" not in cleaned
    assert "Headline" in cleaned


def test_process_generates_hash(tmp_path):
    article = ArticleMetadata(
        id="1",
        source_id="test",
        url="https://example.com",
        title="Title",
        language="und",
        published_at=datetime.now(tz=timezone.utc),
    )
    parser = ParserService(ServiceSettings(service_name="parser-test", object_storage_bucket=str(tmp_path)))

    async def _run():
        content = await parser.process(article, "<p>Hello world</p>")
        assert content.hash is not None
        assert content.metadata.language

    asyncio.run(_run())
