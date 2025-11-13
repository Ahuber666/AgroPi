from __future__ import annotations

from typing import List

from fastapi import FastAPI

from news_core import ArticleContent, ServiceSettings, SummaryArtifact

from .service import VerifierService

app = FastAPI(title="DailyBrief Verifier", version="1.0.0")
service = VerifierService(ServiceSettings(service_name="verifier"))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/verify")
async def verify(event_id: str, summary: SummaryArtifact, articles: List[ArticleContent]):
    return await service.verify(event_id, summary, articles)
