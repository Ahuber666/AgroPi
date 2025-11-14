from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Sequence

from news_core import Event, EventScore, Locale, Slate
from vector_utils import cosine_similarity

from .scoring import RankerConfig, score_event


@dataclass
class SlateBuilder:
    config: RankerConfig = field(default_factory=RankerConfig)
    min_score: float = 0.25
    max_per_source: int = 2
    max_per_country: int = 5
    max_events: int = 12

    def build(
        self,
        events: Sequence[Event],
        locale: Locale,
        topic: str,
        metric_overrides: Dict[str, Dict[str, float]] | None = None,
        user_vec: Sequence[float] | None = None,
    ) -> Slate:
        metric_overrides = metric_overrides or {}
        ranked: List[Event] = []
        per_source: Dict[str, int] = defaultdict(int)
        per_locale: Dict[str, int] = defaultdict(int)

        for event in events:
            metrics = metric_overrides.get(event.id, {})
            metrics.setdefault("locale_match", 1.0 if event.locale == locale else 0.2)
            event_score: EventScore = score_event(event, metrics, self.config)
            if event_score.final < self.min_score:
                continue
            top_source = (event.articles[0].source_id if event.articles else "unknown")
            if per_source[top_source] >= self.max_per_source:
                continue
            if per_locale[event.locale.value] >= self.max_per_country:
                continue
            rerank_bonus = 0.0
            if user_vec and event.topic_vec:
                rerank_bonus = 0.05 * cosine_similarity(user_vec, event.topic_vec)
            event.server_score = min(1.0, event_score.final + rerank_bonus)
            ranked.append(event)
            per_source[top_source] += 1
            per_locale[event.locale.value] += 1
            if len(ranked) >= self.max_events:
                break

        ranked.sort(key=lambda e: e.server_score, reverse=True)
        etag = hashlib.sha256("".join(e.id for e in ranked).encode()).hexdigest()

        return Slate(
            id=f"{locale.value}:{topic}:{int(datetime.now(tz=timezone.utc).timestamp())}",
            locale=locale,
            topic=topic,
            generated_at=datetime.now(tz=timezone.utc),
            events=ranked,
            etag=etag,
        )
