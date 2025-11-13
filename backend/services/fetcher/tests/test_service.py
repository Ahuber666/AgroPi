from datetime import datetime, timezone

from news_core import ArticleMetadata, ServiceSettings

from services.fetcher.app.service import FetcherService


class DummyFetcher(FetcherService):
    async def _fetch_source(self, source):  # type: ignore[override]
        return [
            ArticleMetadata(
                id="1",
                source_id=source.id,
                url="https://example.com",
                title="Title",
                language="en",
                published_at=datetime.now(tz=timezone.utc),
            )
        ]


def test_article_id_stable(tmp_path):
    settings = ServiceSettings(service_name="fetcher-test", object_storage_bucket=str(tmp_path))
    service = DummyFetcher(settings, config_path=tmp_path / "config.json")
    article_id = service._article_id("src", "guid")
    assert article_id == service._article_id("src", "guid")
