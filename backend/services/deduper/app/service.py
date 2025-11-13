from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from loguru import logger

from news_core import ArticleContent, ServiceSettings, configure_logging, configure_tracer
from vector_utils import minhash_signature, simhash


def hamming_distance(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


@dataclass
class DuplicateGroup:
    canonical: str
    duplicates: List[str]


class DeduperService:
    def __init__(self, settings: ServiceSettings, simhash_threshold: int = 8):
        self.settings = settings
        self.simhash_threshold = simhash_threshold
        configure_logging(settings.service_name, settings.log_level)
        configure_tracer(settings)

    def group(self, articles: Iterable[ArticleContent]) -> List[DuplicateGroup]:
        buckets: Dict[Tuple[int, Tuple[int, ...]], List[ArticleContent]] = defaultdict(list)
        for article in articles:
            fingerprint = simhash(article.text)
            signature = tuple(minhash_signature(article.text.split()))
            buckets[(fingerprint, signature)].append(article)
        groups: List[DuplicateGroup] = []
        for (fingerprint, _), chunk in buckets.items():
            chunk.sort(key=lambda c: c.metadata.published_at)
            canonical = chunk[0].metadata.id
            dup_ids = [canonical]
            for entry in chunk[1:]:
                distance = hamming_distance(fingerprint, simhash(entry.text))
                if distance <= self.simhash_threshold:
                    dup_ids.append(entry.metadata.id)
            groups.append(DuplicateGroup(canonical=canonical, duplicates=dup_ids))
            logger.info("dedupe_group", canonical=canonical, size=len(dup_ids))
        return groups
