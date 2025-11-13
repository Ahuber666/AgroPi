from __future__ import annotations

from typing import List

from fastapi import FastAPI

from news_core import ArticleContent, ServiceSettings

from .service import DeduperService, DuplicateGroup

app = FastAPI(title="DailyBrief Deduper", version="1.0.0")
service = DeduperService(ServiceSettings(service_name="deduper"))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/dedupe", response_model=List[DuplicateGroup])
async def dedupe(articles: List[ArticleContent]) -> List[DuplicateGroup]:
    return service.group(articles)
