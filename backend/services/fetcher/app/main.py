from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from news_core import ServiceSettings

from .service import FetcherService

app = FastAPI(title="DailyBrief Fetcher", version="1.0.0")
service = FetcherService(ServiceSettings(service_name="fetcher"), config_path=Path(__file__).parent.parent / "config" / "service.yaml")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/fetch/run")
async def run_cycle() -> dict[str, int]:
    processed = await service.run_cycle()
    return {"processed": processed}


@app.on_event("shutdown")
async def shutdown() -> None:
    await service.close()
