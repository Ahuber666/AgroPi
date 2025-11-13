FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install --no-cache-dir poetry
COPY pyproject.toml README.md ./
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction
COPY . .

CMD ["uvicorn", "services.fetcher.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
