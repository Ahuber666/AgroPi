from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import httpx
from bs4 import BeautifulSoup  # type: ignore
import yaml
from loguru import logger

from news_core import ArticleContent, ArticleMetadata, ObjectStorageClient, PostgresRepository, ServiceSettings
from news_core import SourceRegistry, configure_logging, configure_tracer


class FetcherService:
    """Polls the source registry and fetches raw articles."""

    def __init__(self, settings: ServiceSettings, config_path: Path):
        self.settings = settings
        if config_path.exists() and config_path.suffix == ".json":
            self.config = json.loads(config_path.read_text())
        elif config_path.exists():
            self.config = yaml.safe_load(config_path.read_text()) or {}
        else:
            self.config = {}
        registry_path = Path(self.config.get("source_registry", Path(__file__).parents[2] / "configs" / "sources.yaml"))
        self.registry = SourceRegistry(registry_path)
        self.client = httpx.AsyncClient(headers={"User-Agent": "DailyBriefFetcher/1.0"}, timeout=20.0)
        self.storage = ObjectStorageClient(bucket=settings.object_storage_bucket)
        self.repo = PostgresRepository(settings.postgres_dsn)
        configure_logging(settings.service_name, settings.log_level)
        configure_tracer(settings)

    async def close(self) -> None:
        await self.client.aclose()

    async def run_cycle(self) -> int:
        count = 0
        for source in self.registry.load():
            articles = await self._fetch_source(source)
            for article in articles:
                html_path = await self.storage.store_html(article.id, article.title)
                content = ArticleContent(metadata=article, text=article.title, raw_html_path=html_path)
                await self.repo.upsert_article(content)
                count += 1
        logger.info("fetch_cycle_complete", articles=count)
        return count

    async def _fetch_source(self, source) -> List[ArticleMetadata]:
        if source.rss:
            return await self._fetch_rss(source.id, source.rss)
        if source.json_api:
            return await self._fetch_json(source.id, source.json_api)
        if source.sitemap:
            return await self._fetch_sitemap(source.id, source.sitemap)
        return []

    async def _fetch_rss(self, source_id: str, url: str) -> List[ArticleMetadata]:
        resp = await self.client.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "xml")
        items = []
        for item in soup.find_all("item")[:10]:
            guid = item.guid.text if item.guid else item.link.text
            items.append(
                ArticleMetadata(
                    id=self._article_id(source_id, guid),
                    source_id=source_id,
                    url=item.link.text,
                    title=item.title.text,
                    language="und",
                    published_at=datetime.now(tz=timezone.utc),
                )
            )
        return items

    async def _fetch_json(self, source_id: str, url: str) -> List[ArticleMetadata]:
        resp = await self.client.get(url)
        resp.raise_for_status()
        data = resp.json()
        items = []
        for entry in data.get("articles", [])[:10]:
            items.append(
                ArticleMetadata(
                    id=self._article_id(source_id, entry["url"]),
                    source_id=source_id,
                    url=entry["url"],
                    title=entry.get("title", ""),
                    language=entry.get("language", "und"),
                    published_at=datetime.fromisoformat(entry.get("published_at", datetime.now(tz=timezone.utc).isoformat())),
                )
            )
        return items

    async def _fetch_sitemap(self, source_id: str, url: str) -> List[ArticleMetadata]:
        resp = await self.client.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "xml")
        items = []
        for loc in soup.find_all("loc")[:10]:
            items.append(
                ArticleMetadata(
                    id=self._article_id(source_id, loc.text),
                    source_id=source_id,
                    url=loc.text,
                    title=loc.text.split("/")[-1].replace("-", " "),
                    language="und",
                    published_at=datetime.now(tz=timezone.utc),
                )
            )
        return items

    @staticmethod
    def _article_id(source_id: str, guid: str) -> str:
        return hashlib.sha256(f"{source_id}:{guid}".encode()).hexdigest()


async def bootstrap(config_path: Path) -> FetcherService:
    settings = ServiceSettings(service_name="fetcher")
    service = FetcherService(settings, config_path=config_path)
    return service
