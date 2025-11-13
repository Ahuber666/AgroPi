from __future__ import annotations

from fastapi import FastAPI

from news_core import ServiceSettings

from .schemas import EmbeddingRequest, EmbeddingVector
from .service import EmbeddingsService

app = FastAPI(title="DailyBrief Embeddings", version="1.0.0")
service = EmbeddingsService(ServiceSettings(service_name="embeddings"))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/embed", response_model=list[EmbeddingVector])
async def embed_articles(request: EmbeddingRequest) -> list[EmbeddingVector]:
    return await service.embed(request.articles)
