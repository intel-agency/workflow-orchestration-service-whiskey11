# Architecture — Workflow Orchestration Service

## System Overview

The Workflow Orchestration Service migrates orchestration from a GitHub Actions-embedded model to a standalone, self-hosted, networked client/server architecture.

### End-State Architecture

```
GitHub App (webhooks) → Orchestration Client (FastAPI + Sentinel, :8000)
                           → TCP :4096 →
                         Orchestration Server (opencode serve, Docker, :4096)
```

## Components

### 1. Orchestration Server

The server runs the full orchestration stack inside a Docker container:

- **Technology**: Docker container, opencode CLI, MCP servers
- **Port**: 4096 (opencode serve)
- **Contents**:
  - opencode serve — AI agent server
  - 27 specialist agent definitions (.opencode/agents/)
  - 20 command prompts (.opencode/commands/)
  - MCP servers (sequential-thinking, memory)
  - Shell bridge scripts (devcontainer-opencode.sh, start-opencode-server.sh)
  - Prompt assembly pipeline (assemble-orchestrator-prompt.sh)
  - Agent orchestration config (opencode.json, AGENTS.md)

### 2. Orchestration Client

The client is a Python service that receives GitHub events and dispatches prompts:

- **Technology**: Python 3.12+, FastAPI, httpx, Pydantic
- **Port**: 8000 (webhook receiver)

#### Sub-components:

1. **Webhook Handler (FastAPI)**
   - Receives GitHub App webhooks
   - HMAC SHA-256 verification
   - Event triage → WorkItem creation
   - Adds `agent:queued` label via GitHub API

2. **Sentinel Orchestrator (Polling Loop)**
   - Polls GitHub Issues for `agent:queued` label
   - Assign-then-verify distributed locking
   - Shell bridge dispatch via devcontainer-opencode.sh
   - Heartbeat comments (5-min interval)
   - Status label lifecycle management

3. **Shared Components**
   - WorkItem model (Pydantic, credential scrubbing)
   - GitHub Queue (ITaskQueue ABC, GitHubQueue implementation)
   - Configuration module (env var based)

### 3. GitHub App

Delivers repository events as webhooks to the client:

- Events: issues.labeled, issues.opened, pull_request.*, workflow_dispatch
- HMAC SHA-256 verification

## Data Flow

### Happy Path

```
1. GitHub App fires webhook → POST /webhooks/github (Client)
2. Client verifies HMAC SHA-256 signature
3. Client triages event → creates WorkItem
4. Client adds agent:queued label via GitHub API
5. Sentinel polling loop detects queued issue
6. Sentinel claims task (assign-then-verify pattern)
7. Sentinel updates label: agent:queued → agent:in-progress
8. Sentinel calls: devcontainer-opencode.sh prompt -p "<instruction>" -u <server-url>
9. Shell bridge invokes: opencode run --attach <server-url> --agent orchestrator "<prompt>"
10. Orchestrator agent executes workflow, delegates to specialists
11. On completion: Sentinel updates label → agent:success, posts summary comment
12. Sentinel resets environment, returns to polling
```

## Design Principles

1. **Shell Bridge as Primary API** (ADR-07): The Sentinel interacts with the server exclusively via devcontainer-opencode.sh. No Docker SDK reimplementation.
2. **Polling-First Resiliency** (ADR-08): Webhook delivery is an optimization; polling ensures self-healing on restart.
3. **Provider-Agnostic Queue** (ADR-09): All queue interactions go through ITaskQueue ABC — GitHub today, Linear/Jira later.
4. **Credential Scrubbing** (R-7): All output posted to GitHub is sanitized via scrub_secrets() before posting.

## Security Model

- HMAC webhook verification (SHA-256)
- Credential scrubbing on all GitHub-posted content
- Container isolation (no shared host resources)
- Minimum token scopes (repo, workflow, project, read:org)
- No secrets in code — all via environment variables

## Project Structure

```
/
├── client/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                    # Entry point: dual-mode (webhook + polling)
│   │   ├── config.py                  # Centralized configuration
│   │   ├── sentinel.py                # Sentinel Orchestrator
│   │   ├── notifier.py                # Webhook Handler (FastAPI)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── work_item.py           # WorkItem, TaskType, WorkItemStatus
│   │   └── queue/
│   │       ├── __init__.py
│   │       └── github_queue.py        # ITaskQueue, GitHubQueue
│   ├── scripts/
│   │   └── devcontainer-opencode.sh   # Local copy for remote dispatch
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── Dockerfile
├── server/                            # Server is built from root Dockerfile
│   └── (uses root-level .opencode/, scripts/, etc.)
├── plan_docs/                         # Project planning documents
├── scripts/                           # Shared scripts (shell bridge, etc.)
├── test/                              # Test suite
├── docs/                              # Documentation
├── .opencode/                         # Agent definitions & commands
├── docker-compose.yml                 # Local dev orchestration
├── AGENTS.md                          # Agent instructions
└── opencode.json                      # opencode configuration
```
