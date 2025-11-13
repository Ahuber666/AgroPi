from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict

from loguru import logger

from .models import ArticleContent, ArticleMetadata, Event


class PostgresRepository:
    """Simplified async repository that hides persistence logic."""

    def __init__(self, dsn: str):
        self._dsn = dsn
        self._mock_store: Dict[str, Dict[str, Any]] = {"article": {}, "event": {}}

    async def upsert_article(self, article: ArticleContent) -> None:
        logger.debug("upsert_article", article_id=article.metadata.id)
        await asyncio.sleep(0)
        self._mock_store["article"][article.metadata.id] = article.model_dump()

    async def store_event(self, event: Event) -> None:
        logger.debug("store_event", event_id=event.id)
        await asyncio.sleep(0)
        self._mock_store["event"][event.id] = event.model_dump()

    async def fetch_article(self, article_id: str) -> ArticleMetadata | None:
        payload = self._mock_store["article"].get(article_id)
        if not payload:
            return None
        return ArticleContent(**payload).metadata


class ObjectStorageClient:
    """Thin wrapper around cloud storage; defaults to local disk for dev."""

    def __init__(self, bucket: str, base_path: str | None = None):
        self._bucket = bucket
        self._base_path = Path(base_path or ".cache/object_store")
        self._base_path.mkdir(parents=True, exist_ok=True)

    async def store_html(self, article_id: str, html: str) -> str:
        path = self._base_path / f"{article_id}.html"
        path.write_text(html)
        logger.debug("stored_raw_html", article_id=article_id, bucket=self._bucket, path=str(path))
        await asyncio.sleep(0)
        return str(path)

    async def store_json(self, key: str, payload: Dict[str, Any]) -> str:
        path = self._base_path / f"{key}.json"
        path.write_text(str(payload))
        logger.debug("stored_json", key=key, bucket=self._bucket)
        await asyncio.sleep(0)
        return str(path)
