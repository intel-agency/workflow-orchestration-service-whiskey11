FROM python:3.12-slim

LABEL org.opencontainers.image.title="Workflow Orchestration Client" \
      org.opencontainers.image.description="FastAPI webhook handler and Sentinel polling orchestrator" \
      org.opencontainers.image.source="https://github.com/intel-agency/workflow-orchestration-service-whiskey11"

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash git curl && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy requirements first for layer caching — dependency changes are less
# frequent than source changes, so this layer is reused across builds.
COPY requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Copy source code (must be before editable install)
COPY . .

# Editable install so the package is importable via `python -m src.main`
RUN uv pip install --system --no-cache-dir -e .

# Run as non-root user for production security
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "src.main"]
