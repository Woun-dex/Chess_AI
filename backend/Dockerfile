# Multi-stage Dockerfile for Chess AI Backend + Stockfish
FROM python:3.12-slim-bookworm AS base

# Install system dependencies including Stockfish and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    stockfish \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for rapid Python packaging
COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Copy dependency manifests first for layer caching
COPY pyproject.toml README.md ./

# Install dependencies using uv sync
RUN uv venv && uv pip install -e ".[dev]"

# Copy application source
COPY src/ ./src/
COPY tests/ ./tests/
COPY ruff.toml ./
COPY alembic.ini ./
COPY migrations/ ./migrations/
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]

EXPOSE 8000

CMD ["uvicorn", "chess_ai.presentation.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
