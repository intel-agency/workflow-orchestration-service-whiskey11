# Technology Stack — Workflow Orchestration Service

## Languages & Runtimes

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12+ | Primary language for client service, models, queue |
| Bash | 5.x | Shell bridge scripts, entrypoints, bootstrap |
| PowerShell | 7.x | Validation scripts, label management, CI tooling |

## Frameworks & Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| FastAPI | >=0.115.0 | Async webhook handler with Pydantic validation, auto-OpenAPI |
| Pydantic | >=2.9.0 | Data models (WorkItem, TaskType, WorkItemStatus), credential scrubbing |
| httpx | >=0.27.0 | Async HTTP client for GitHub API interactions |
| uvicorn[standard] | >=0.30.0 | ASGI server for FastAPI application |

## Agent Runtime

| Component | Version | Purpose |
|-----------|---------|---------|
| opencode CLI | 1.2.24 | AI agent runtime, server mode, MCP server host |
| MCP sequential-thinking | latest | Structured thinking for agent decision-making |
| MCP memory | latest | Knowledge graph persistence (JSONL file-based) |

## Package Management

| Tool | Version | Purpose |
|------|---------|---------|
| uv | 0.10.9+ | Python package manager (Rust-based, fast) |

## Containerization

| Technology | Purpose |
|-----------|---------|
| Docker | Server container (opencode serve + agents + MCP) |
| Docker Compose | Local development orchestration (server + client) |
| GitHub Container Registry (GHCR) | Prebuilt devcontainer images |

## CI/CD & Quality

| Tool | Purpose |
|------|---------|
| GitHub Actions | CI validation (lint, scan, test) |
| actionlint | Workflow YAML linting |
| gitleaks | Secret detection |
| markdownlint | Markdown linting |
| ShellCheck | Shell script linting |
| Pester | PowerShell test framework |

## Development Tools

| Tool | Purpose |
|------|---------|
| gh CLI | GitHub API interactions |
| Node.js 24 LTS | Required for MCP server packages (npx) |
| .NET SDK 10 | Available in devcontainer (prebuilt image) |
| Bun 1.3.10 | Available in devcontainer (prebuilt image) |

## External Services

| Service | Purpose |
|---------|---------|
| GitHub App | Webhook delivery for repository events |
| GitHub API | Issue tracking, PR management, label lifecycle |
| ZhipuAI GLM | AI model provider (glm-5, glm-4.7) |
| OpenAI | AI model provider (gpt-5.4, gpt-5.4-mini) |
| Kimi (Moonshot) | AI model provider (kimi-k2-thinking) |
| Google Gemini | AI model provider (gemini-3.1-pro) |
