from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List

from loguru import logger

from news_core import ArticleMetadata, Event, Locale, ServiceSettings, configure_logging, configure_tracer
from vector_utils import cosine_similarity


def _resolve_locale(article: ArticleMetadata) -> Locale:
    try:
        return Locale(article.language)
    except ValueError:
        return Locale.EN_US


class ClustererService:
    def __init__(self, settings: ServiceSettings, similarity_threshold: float = 0.85):
        self.settings = settings
        self.similarity_threshold = similarity_threshold
        configure_logging(settings.service_name, settings.log_level)
        configure_tracer(settings)

    def cluster(self, articles: List[ArticleMetadata], vectors: List[List[float]]) -> List[Event]:
        if not articles:
            return []
        buckets: Dict[int, List[int]] = defaultdict(list)
        for idx, (article, vec) in enumerate(zip(articles, vectors)):
            assigned = False
            for bucket_id, member_indices in buckets.items():
                anchor_idx = member_indices[0]
                if cosine_similarity(vectors[anchor_idx], vec) >= self.similarity_threshold:
                    member_indices.append(idx)
                    assigned = True
                    break
            if not assigned:
                buckets[idx].append(idx)
        events: List[Event] = []
        for bucket in buckets.values():
            bucket_articles = [articles[i] for i in bucket]
            topic = bucket_articles[0].tags[0] if bucket_articles[0].tags else "general"
            topic_distribution = {topic: 1.0}
            event_id = hashlib.sha256("".join(a.id for a in bucket_articles).encode()).hexdigest()
            events.append(
                Event(
                    id=event_id,
                    title=bucket_articles[0].title,
                    topic=topic,
                    articles=bucket_articles,
                    summary=None,
                    topic_distribution=topic_distribution,
                    locale=_resolve_locale(bucket_articles[0]),
                    burst_score=float(len(bucket_articles)),
                    confidence=min(1.0, len(bucket_articles) / 5),
                    taxonomy=[topic.title()],
                )
            )
            logger.info("cluster_created", event_id=event_id, size=len(bucket))
        return events
