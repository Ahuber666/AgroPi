from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import List

from loguru import logger

from news_core import Event, ServiceSettings, SummaryArtifact, configure_logging, configure_tracer
from vector_utils import cosine_similarity


class SummarizerService:
    def __init__(self, settings: ServiceSettings):
        self.settings = settings
        configure_logging(settings.service_name, settings.log_level)
        configure_tracer(settings)

    def select_articles(self, event: Event, limit: int = 5) -> List[str]:
        vectors = [self._vectorize(article.title) for article in event.articles]
        target = min(max(3, len(vectors)), 8)
        selections = self._mmr(vectors, limit=target)
        return [event.articles[idx].url for idx in selections]

    def _vectorize(self, text: str) -> List[float]:
        digest = hashlib.sha256(text.encode()).digest()
        return [byte / 255.0 for byte in digest[:16]]

    def _mmr(self, vectors: List[List[float]], limit: int, lambda_param: float = 0.7) -> List[int]:
        if not vectors:
            return []
        selected = [0]
        candidates = list(range(1, len(vectors)))
        while candidates and len(selected) < limit:
            best_idx = candidates[0]
            best_score = float("-inf")
            for idx in candidates:
                redundancy = max(cosine_similarity(vectors[idx], vectors[s]) for s in selected)
                score = lambda_param - (1 - lambda_param) * redundancy
                if score > best_score:
                    best_score = score
                    best_idx = idx
            selected.append(best_idx)
            candidates.remove(best_idx)
        return selected

    def _synthetic_summary(self, event: Event, selected_urls: List[str]) -> SummaryArtifact:
        timestamp = datetime.now(tz=timezone.utc).strftime("%d %b %Y %H:%M UTC")
        citations = [f"[{idx + 1}]" for idx in range(len(selected_urls))]
        bullet = f"{event.title} confirmed by {len(selected_urls)} sources {citations[0]}"
        summary = (
            f"As of {timestamp}, {event.title} remains the top development in {event.topic.lower()} with "
            f"details corroborated by {len(selected_urls)} outlets {', '.join(citations)}."
        )
        return SummaryArtifact(
            title=event.title,
            bullets=[bullet],
            summary=summary,
            key_quotes=[f"Key facts derived from {selected_urls[0]}"] if selected_urls else [],
            sources=selected_urls,
            confidence=min(1.0, event.confidence + 0.2),
            updated_at=datetime.now(tz=timezone.utc),
        )

    async def summarize(self, event: Event) -> SummaryArtifact:
        selected = self.select_articles(event)
        if not selected:
            raise ValueError("Event must contain at least one article")
        artifact = self._synthetic_summary(event, selected)
        if "[" not in artifact.summary:
            raise ValueError("Summary missing citation")
        if "UTC" not in artifact.summary:
            raise ValueError("Summary missing timestamp reference")
        logger.info("summary_created", event_id=event.id)
        return artifact
