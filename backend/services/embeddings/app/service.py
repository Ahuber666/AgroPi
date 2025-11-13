from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from loguru import logger

from news_core import ArticleContent, ServiceSettings, configure_logging, configure_tracer
from vector_utils import LocalEncoder

from .schemas import EmbeddingVector


class EmbeddingsService:
    def __init__(self, settings: ServiceSettings, dimension: int = 32):
        self.settings = settings
        self.encoder = LocalEncoder(dim=dimension)
        configure_logging(settings.service_name, settings.log_level)
        configure_tracer(settings)

    async def embed(self, articles: List[ArticleContent]) -> List[EmbeddingVector]:
        vectors = self.encoder.encode([article.text for article in articles]) if articles else []
        payload = []
        for article, vector in zip(articles, vectors):
            payload.append(
                EmbeddingVector(
                    article_id=article.metadata.id,
                    vector=vector,
                    generated_at=datetime.now(tz=timezone.utc),
                )
            )
            logger.info("embedding_generated", article_id=article.metadata.id)
        return payload
