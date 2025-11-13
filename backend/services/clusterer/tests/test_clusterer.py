from datetime import datetime, timezone

from news_core import ArticleMetadata, ServiceSettings
from vector_utils import LocalEncoder

from services.clusterer.app.service import ClustererService


encoder = LocalEncoder()


def build_article(idx: str, text: str) -> ArticleMetadata:
    return ArticleMetadata(
        id=idx,
        source_id="src",
        url="https://example.com",
        title=text,
        language="en-US",
        published_at=datetime.now(tz=timezone.utc),
    )


def test_cluster_groups_similar_articles():
    service = ClustererService(ServiceSettings(service_name="clusterer-test"), similarity_threshold=0.7)
    articles = [build_article("a", "Breaking news"), build_article("b", "Breaking news"), build_article("c", "Other story")]
    vectors = encoder.encode([a.title for a in articles])
    events = service.cluster(articles, vectors)
    assert any(len(event.articles) >= 2 for event in events)
