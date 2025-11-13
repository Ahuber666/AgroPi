from __future__ import annotations

from fastapi import FastAPI

from news_core import ServiceSettings

from .schemas import ClusterArticle, ClusterResponse
from .service import ClustererService

app = FastAPI(title="DailyBrief Clusterer", version="1.0.0")
service = ClustererService(ServiceSettings(service_name="clusterer"))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/cluster", response_model=ClusterResponse)
async def cluster(payload: list[ClusterArticle]) -> ClusterResponse:
    articles = [item.metadata for item in payload]
    vectors = [item.vector for item in payload]
    events = service.cluster(articles, vectors)
    return ClusterResponse(events=events)
