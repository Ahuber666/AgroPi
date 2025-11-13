from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import yaml

from .models import Source


class SourceRegistry:
    """Loads and filters source definitions used by Fetcher."""

    def __init__(self, path: Path):
        self._path = path

    def load(self) -> List[Source]:
        if not self._path.exists():
            raise FileNotFoundError(f"Registry file {self._path} missing")
        payload = yaml.safe_load(self._path.read_text())
        sources = [Source(**entry) for entry in payload.get("sources", [])]
        return sorted(sources, key=lambda s: (s.priority, s.name))

    def filter_by_locale(self, locale: str) -> Iterable[Source]:
        locale = locale.lower()
        for src in self.load():
            if src.locale.value.lower() == locale:
                yield src
