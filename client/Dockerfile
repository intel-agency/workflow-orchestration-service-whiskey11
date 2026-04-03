FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash git && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy source code (must be before editable install)
COPY . .

RUN uv pip install --system -e .

EXPOSE 8000
CMD ["python", "-m", "src.main"]
