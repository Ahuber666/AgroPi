from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Sequence

from loguru import logger

from news_core import Event, Locale, ServiceSettings, Slate, configure_logging, configure_tracer
from ranking_lib import RankerConfig, SlateBuilder


class RankerService:
    def __init__(self, settings: ServiceSettings, config: RankerConfig | None = None):
        self.settings = settings
        self.builder = SlateBuilder(config=config or RankerConfig())
        configure_logging(settings.service_name, settings.log_level)
        configure_tracer(settings)

    def build_slates(self, events: Sequence[Event], locales: Iterable[Locale]) -> Dict[str, List[Slate]]:
        grouped: Dict[str, List[Slate]] = defaultdict(list)
        for locale in locales:
            for topic in {event.topic for event in events}:
                topic_events = [event for event in events if event.topic == topic]
                slate = self.builder.build(topic_events, locale=locale, topic=topic)
                grouped[locale.value].append(slate)
                logger.info("slate_built", locale=locale.value, topic=topic, events=len(slate.events))
        return grouped
