from datetime import datetime, timezone

from news_core import ArticleContent, ArticleMetadata, ServiceSettings

from services.deduper.app.service import DeduperService


def build_article(article_id: str, text: str) -> ArticleContent:
    return ArticleContent(
        metadata=ArticleMetadata(
            id=article_id,
            source_id="src",
            url="https://example.com",
            title="Title",
            language="en",
            published_at=datetime.now(tz=timezone.utc),
        ),
        text=text,
        raw_html_path="/tmp",
    )


def test_group_merges_duplicates():
    service = DeduperService(ServiceSettings(service_name="deduper-test"), simhash_threshold=10)
    groups = service.group([
        build_article("a", "Breaking news event happens today"),
        build_article("b", "Breaking news event happens today"),
        build_article("c", "Completely different story"),
    ])
    merged = next(g for g in groups if g.canonical == "a")
    assert set(merged.duplicates) == {"a", "b"}
