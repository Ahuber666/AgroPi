from __future__ import annotations

from fastapi import FastAPI

from news_core import ServiceSettings

from .schemas import ParseRequest
from .service import ParserService

app = FastAPI(title="DailyBrief Parser", version="1.0.0")
service = ParserService(ServiceSettings(service_name="parser"))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/parse")
async def parse_article(request: ParseRequest) -> dict[str, str]:
    content = await service.process(request.article, request.html)
    return {"hash": content.hash or "", "language": content.metadata.language}
