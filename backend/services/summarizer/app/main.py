from __future__ import annotations

from fastapi import FastAPI

from news_core import Event, ServiceSettings

from .service import SummarizerService

app = FastAPI(title="DailyBrief Summarizer", version="1.0.0")
service = SummarizerService(ServiceSettings(service_name="summarizer"))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/summarize")
async def summarize(event: Event) -> dict[str, str]:
    artifact = await service.summarize(event)
    return {"title": artifact.title, "summary": artifact.summary}
