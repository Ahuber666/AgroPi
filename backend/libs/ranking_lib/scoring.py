from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict

from news_core import Event, EventScore
from vector_utils import jensen_shannon


def _safe(value: float) -> float:
    if math.isnan(value) or math.isinf(value):
        return 0.0
    return value


@dataclass
class RankerConfig:
    w_recency: float = 0.23
    w_sources: float = 0.15
    w_diversity: float = 0.1
    w_geo: float = 0.07
    w_interest: float = 0.18
    w_impact: float = 0.15
    w_novelty: float = 0.12
    tau_hours: float = 12.0
    disagreement_penalty: float = 0.7

    @classmethod
    def from_dict(cls, payload: Dict[str, float]) -> "RankerConfig":
        return cls(**payload)


def score_event(event: Event, metrics: Dict[str, float], config: RankerConfig | None = None) -> EventScore:
    config = config or RankerConfig()
    hours_since_peak = metrics.get("hours_since_peak", 0.0)
    unique_sources = metrics.get("unique_sources", len(event.articles))
    unique_reputable_sources = metrics.get("unique_reputable_sources", unique_sources)
    locale_match = metrics.get("locale_match", 1.0)
    ctr = metrics.get("ctr", 0.05)
    dwell = metrics.get("dwell", 0.5)
    impact = metrics.get("impact", 0.5)
    novelty = metrics.get("novelty", 0.5)
    disagreement = metrics.get("disagreement", 0.0)
    topic_distribution = list(event.topic_distribution.values()) or [1.0]

    recency_score = config.w_recency * math.exp(-hours_since_peak / max(config.tau_hours, 1e-6))
    sources_score = config.w_sources * math.log(1 + unique_reputable_sources)
    diversity_score = config.w_diversity * jensen_shannon(topic_distribution)
    geo_score = config.w_geo * locale_match
    interest_score = config.w_interest * math.sqrt(max(ctr, 0) * max(dwell, 0))
    impact_score = config.w_impact * impact
    novelty_score = config.w_novelty * (1 - novelty)
    penalty = config.disagreement_penalty if disagreement > 0.4 else 1.0

    final = (recency_score + sources_score + diversity_score + geo_score + interest_score + impact_score + novelty_score) * penalty

    return EventScore(
        recency=_safe(recency_score),
        sources=_safe(sources_score),
        diversity=_safe(diversity_score),
        geo=_safe(geo_score),
        interest=_safe(interest_score),
        impact=_safe(impact_score),
        novelty=_safe(novelty_score),
        final=_safe(min(1.0, final)),
    )
