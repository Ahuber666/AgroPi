from __future__ import annotations

import re
from typing import Dict, List

from loguru import logger

from news_core import ArticleContent, ServiceSettings, SummaryArtifact, VerificationResult, configure_logging, configure_tracer


class VerifierService:
    def __init__(self, settings: ServiceSettings, threshold: float = 0.35):
        self.settings = settings
        self.threshold = threshold
        configure_logging(settings.service_name, settings.log_level)
        configure_tracer(settings)

    def _score_sentence(self, sentence: str, articles: List[ArticleContent]) -> float:
        sentence_lower = sentence.lower()
        matches = sum(1 for article in articles if sentence_lower.split(" ")[0] in article.text.lower())
        return min(1.0, matches / max(1, len(articles)))

    def _check_numbers(self, sentence: str, articles: List[ArticleContent]) -> bool:
        numbers = re.findall(r"\d+", sentence)
        if not numbers:
            return True
        return any(number in article.text for article in articles for number in numbers)

    async def verify(self, event_id: str, summary: SummaryArtifact, articles: List[ArticleContent]) -> VerificationResult:
        sentence_scores: Dict[int, float] = {}
        numeric_checks: Dict[str, bool] = {}
        disputed = False
        for idx, sentence in enumerate(summary.summary.split(". ")):
            score = self._score_sentence(sentence, articles)
            sentence_scores[idx] = score
            numeric_checks[str(idx)] = self._check_numbers(sentence, articles)
            if score < self.threshold or not numeric_checks[str(idx)]:
                disputed = True
        confidence = sum(sentence_scores.values()) / max(1, len(sentence_scores))
        logger.info("verification_complete", event_id=event_id, disputed=disputed)
        return VerificationResult(
            event_id=event_id,
            disputed=disputed,
            confidence=confidence,
            sentence_scores=sentence_scores,
            numeric_checks=numeric_checks,
        )
