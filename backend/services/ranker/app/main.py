from __future__ import annotations

from typing import List

from fastapi import FastAPI

from news_core import Event, Locale, ServiceSettings, Slate

from .service import RankerService

app = FastAPI(title="DailyBrief Ranker", version="1.0.0")
service = RankerService(ServiceSettings(service_name="ranker"))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/slates", response_model=dict[str, List[Slate]])
async def slates(events: List[Event], locales: List[Locale]) -> dict[str, List[Slate]]:
    return service.build_slates(events, locales)
