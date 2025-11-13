# DailyBrief Backend

DailyBrief's backend is a Python-first monorepo that packages ten microservices plus three shared libraries.  Each service owns its own deployment artifact (Dockerfile + Helm friendly config) while sharing a consistent FastAPI/async toolkit, observability primitives, and domain models under `libs/`.

## Layout

```
backend/
├── libs/
│   ├── news_core          # Pydantic domain models, schemas and messaging contracts
│   ├── vector_utils       # Embedding helpers, SimHash/MinHash, divergence math
│   └── ranking_lib        # Production ranking pipeline primitives
├── services/
│   ├── fetcher            # Multi-source ingestion
│   ├── parser             # Boilerplate stripping + normalization
│   ├── deduper            # SimHash/MinHash canonicalization
│   ├── embeddings         # Batch embedding generation + vector DB writes
│   ├── clusterer          # Even graph clustering + burst detection
│   ├── summarizer         # Event summarization + guardrails
│   ├── verifier           # Summary verification + dispute tracking
│   ├── ranker             # Learning-to-rank scorer + slate builder
│   ├── api_gateway        # GraphQL API + asset REST endpoints
│   └── admin_console      # Next.js based admin UI
├── docker-compose.yml     # Local orchestration of the microservices
└── pyproject.toml         # Shared dependency lock + tooling config
```

## Local development

1. Install Poetry (`pipx install poetry`).
2. From the `backend/` folder install deps: `poetry install`.
3. Start individual services with `poetry run uvicorn services.fetcher.app.main:app` etc, or boot the full stack via `docker compose up`.
4. Run unit tests with `poetry run pytest` (fixtures live inside each service).

Each microservice exposes `/health` and `/metrics` endpoints, ships OpenTelemetry exporters, and pushes Prometheus metrics by default.  Configuration derives from `.env` + `config/service.yaml` per service; see the examples under `services/*/config`.
