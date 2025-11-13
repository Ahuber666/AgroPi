from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Header
from fastapi.responses import FileResponse, JSONResponse
from strawberry.fastapi import GraphQLRouter

from news_core import Locale, ServiceSettings

from .schema import SlateType, build_schema
from .service import GatewayService

settings = ServiceSettings(service_name="api-gateway")
service = GatewayService(settings)
schema, context = build_schema(service)

app = FastAPI(title="DailyBrief API Gateway", version="1.0.0")
app.include_router(GraphQLRouter(schema, context_getter=lambda request: context), prefix="/graphql")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/slates")
async def slate_endpoint(locale: Locale, topics: str, if_none_match: Optional[str] = Header(default=None)):
    topic_list = [topic.strip() for topic in topics.split(",") if topic.strip()]
    slates = service.get_slates(locale, topic_list)
    etag = slates[0].etag if slates else "0"
    if if_none_match == etag:
        return JSONResponse(status_code=304, content=None)
    payload = [
        {
            "id": slate.id,
            "locale": slate.locale.value,
            "topic": slate.topic,
            "generated_at": slate.generated_at.isoformat(),
            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                    "topic": event.topic,
                    "summary": event.summary,
                    "confidence": event.confidence,
                    "server_score": event.server_score,
                }
                for event in slate.events
            ],
            "etag": slate.etag,
        }
        for slate in slates
    ]
    return JSONResponse(
        content={"slates": payload},
        headers={
            "ETag": etag,
            "Last-Modified": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
        },
    )


@app.get("/assets/sources/{source_id}")
async def source_logo(source_id: str):
    path = service.get_source_logo(source_id)
    return FileResponse(path, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})
