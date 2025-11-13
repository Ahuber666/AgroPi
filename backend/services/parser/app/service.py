from __future__ import annotations

import hashlib
from pathlib import Path

from bs4 import BeautifulSoup  # type: ignore
from langdetect import detect  # type: ignore
from loguru import logger

from news_core import ArticleContent, ArticleMetadata, PostgresRepository, ServiceSettings, configure_logging, configure_tracer


class ParserService:
    def __init__(self, settings: ServiceSettings):
        self.settings = settings
        self.repo = PostgresRepository(settings.postgres_dsn)
        configure_logging(settings.service_name, settings.log_level)
        configure_tracer(settings)

    def normalize_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        for aside in soup.find_all(class_="ad"):
            aside.extract()
        return " ".join(soup.get_text(separator=" ").split())

    async def process(self, article: ArticleMetadata, raw_html: str) -> ArticleContent:
        cleaned = self.normalize_html(raw_html)
        language = detect(cleaned[:500]) if cleaned else "und"
        digest = hashlib.sha256(cleaned.encode()).hexdigest()
        content = ArticleContent(
            metadata=article.copy(update={"language": language}),
            text=cleaned,
            raw_html_path=f"s3://{self.settings.object_storage_bucket}/{article.id}.html",
            hash=digest,
        )
        await self.repo.upsert_article(content)
        logger.info("article_normalized", article_id=article.id, language=language)
        return content
