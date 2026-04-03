# Workflow Orchestration Service

A standalone client/server orchestration service that migrates orchestration from GitHub Actions to a self-hosted model.

## Architecture

- **Orchestration Server**: Docker container running `opencode serve` with AI agents, MCP servers, and shell bridge scripts (port 4096)
- **Orchestration Client**: Python FastAPI service with webhook handler and Sentinel polling orchestrator (port 8000)
- **GitHub App**: Delivers repository events as webhooks to the client

## Quick Start

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- `uv` package manager

### Local Development

```bash
# Install client dependencies
cd client && uv pip install -e . && cd ..

# Run validation
pwsh -NoProfile -File ./scripts/validate.ps1 -All

# Start services with Docker Compose
docker compose up
```

## Validation

```bash
# All checks
pwsh -NoProfile -File ./scripts/validate.ps1 -All

# Individual checks
pwsh -NoProfile -File ./scripts/validate.ps1 -Lint
pwsh -NoProfile -File ./scripts/validate.ps1 -Scan
pwsh -NoProfile -File ./scripts/validate.ps1 -Test
```

## Project Structure

See [Architecture Documentation](plan_docs/architecture.md) for the full project structure.

## Documentation

- [Architecture](plan_docs/architecture.md)
- [Tech Stack](plan_docs/tech-stack.md)
- [Implementation Plan](plan_docs/workflow-plan.md)
- [Implementation Specification](plan_docs/Application%20Implementation%20Specification%20-%20workflow-orchestration-service%20v1.2.md)
