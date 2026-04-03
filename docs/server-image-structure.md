# Server Image Directory Structure

> Canonical filesystem layout for the orchestration server image, built in the external
> [`intel-agency/workflow-orchestration-prebuild`](https://github.com/intel-agency/workflow-orchestration-prebuild) repository.

## Root: `/opt/orchestration/`

All orchestration files are installed under this deterministic root. The `ORCHESTRATION_ROOT`
environment variable defaults to this path; scripts resolve their paths relative to it.

```
/opt/orchestration/
├── .opencode/
│   ├── agents/                          # Agent definitions (18 files)
│   │   ├── agent-instructions-expert.md
│   │   ├── backend-developer.md
│   │   ├── cloud-infra-expert.md
│   │   ├── code-reviewer.md
│   │   ├── database-admin.md
│   │   ├── debugger.md
│   │   ├── developer.md
│   │   ├── devops-engineer.md
│   │   ├── documentation-expert.md
│   │   ├── frontend-developer.md
│   │   ├── github-expert.md
│   │   ├── odbplusplus-expert.md
│   │   ├── orchestrator.md
│   │   ├── planner.md
│   │   ├── product-manager.md
│   │   ├── qa-test-engineer.md
│   │   ├── researcher.md
│   │   └── ux-ui-designer.md
│   ├── commands/                        # Reusable command prompts (20 files)
│   │   ├── analyze-progress-doc.md
│   │   ├── assign.md
│   │   ├── continue-orchestrating-project-setup.md
│   │   ├── create-app-from-plans.md
│   │   ├── create-app-plan.md
│   │   ├── create-application.md
│   │   ├── create-new-ai-app-spec.md
│   │   ├── create-repo-custom-instructions.md
│   │   ├── create-repo-summary.md
│   │   ├── fix-failing-workflows.md
│   │   ├── general.md
│   │   ├── grind-pr-reviews.md
│   │   ├── orchestrate-dynamic-workflow.md
│   │   ├── orchestrate-new-project.md
│   │   ├── orchestrate-project-setup.md
│   │   ├── optimize-prompt.md
│   │   ├── pr-review-comments-model-pr-num.md
│   │   ├── pr-review-comments.md
│   │   ├── prompt-gemini-model.md
│   │   └── resolve-pr-comments.md
│   ├── .gitignore
│   └── package.json
├── .github/
│   └── workflows/
│       └── prompts/
│           └── orchestrator-agent-prompt.md  # Prompt template with __EVENT_DATA__ placeholder
├── .assembled-orchestrator-prompt.md    # Assembled prompt (generated at runtime by assemble-orchestrator-prompt.sh)
├── scripts/                             # Shell bridge and utility scripts (5 primary)
│   ├── devcontainer-opencode.sh         # Primary CLI wrapper for devcontainer orchestration
│   ├── assemble-orchestrator-prompt.sh  # Assembles prompt from template + event data
│   ├── start-opencode-server.sh         # Starts opencode serve (setsid daemon)
│   ├── resolve-image-tags.sh            # Resolves devcontainer image tags
│   └── run_opencode_prompt.sh           # Validates API keys, runs opencode with watchdog
├── .memory/                             # MCP knowledge graph persistence (JSONL)
│   └── memory.jsonl
├── opencode.json                        # opencode config: models, MCP servers, tool permissions
├── AGENTS.md                            # Agent instructions and project documentation
└── local_ai_instruction_modules/        # Local instruction modules
    ├── ai-core-instructions.md
    ├── ai-development-instructions.md
    ├── ai-dynamic-workflows.md
    ├── ai-terminal-commands.md
    └── ai-workflow-assignments.md
```

## File Inventory

### Agents (18 files)

| # | File | Purpose |
|---|------|---------|
| 1 | `agent-instructions-expert.md` | Retrieves and inserts canonical agent instructions |
| 2 | `backend-developer.md` | Backend API design, service architecture, system reliability |
| 3 | `cloud-infra-expert.md` | Cloud infrastructure, IaC, governance controls |
| 4 | `code-reviewer.md` | Code reviews: correctness, security, performance, docs |
| 5 | `database-admin.md` | Relational/NoSQL data store design and optimization |
| 6 | `debugger.md` | Reproduces issues, writes minimal failing tests, proposes fixes |
| 7 | `developer.md` | Generalist: small cross-cutting enhancements with quality safeguards |
| 8 | `devops-engineer.md` | CI/CD pipelines, environments, automation, observability |
| 9 | `documentation-expert.md` | Developer and user docs, quickstarts, runbooks |
| 10 | `frontend-developer.md` | Accessible, performant UI components and flows |
| 11 | `github-expert.md` | GitHub workflow automation, PR management, repo operations |
| 12 | `odbplusplus-expert.md` | ODB++ spec and OdbDesign codebase expert |
| 13 | `orchestrator.md` | Coordinates specialists, never writes code directly |
| 14 | `planner.md` | Converts strategic goals into sequenced milestones |
| 15 | `product-manager.md` | Outcome-oriented strategist, captures customer value |
| 16 | `qa-test-engineer.md` | Test strategies, validation suites, quality gates |
| 17 | `researcher.md` | Background research, best practices, competitive analysis |
| 18 | `ux-ui-designer.md` | Wireframes, flows, accessibility, design QA |

### Commands (20 files)

| # | File | Purpose |
|---|------|---------|
| 1 | `analyze-progress-doc.md` | Analyzes progress documentation |
| 2 | `assign.md` | Assigns tasks to agents |
| 3 | `continue-orchestrating-project-setup.md` | Continues project setup orchestration |
| 4 | `create-app-from-plans.md` | Creates application from plan docs |
| 5 | `create-app-plan.md` | Creates application plan |
| 6 | `create-application.md` | Creates application scaffold |
| 7 | `create-new-ai-app-spec.md` | Creates new AI app specification |
| 8 | `create-repo-custom-instructions.md` | Creates repository custom instructions |
| 9 | `create-repo-summary.md` | Creates repository summary |
| 10 | `fix-failing-workflows.md` | Fixes failing GitHub Actions workflows |
| 11 | `general.md` | General-purpose command |
| 12 | `grind-pr-reviews.md` | Batch PR review processing |
| 13 | `orchestrate-dynamic-workflow.md` | Orchestrates dynamic workflow execution |
| 14 | `orchestrate-new-project.md` | Orchestrates new project setup |
| 15 | `orchestrate-project-setup.md` | Orchestrates project setup |
| 16 | `optimize-prompt.md` | Optimizes agent prompts |
| 17 | `pr-review-comments-model-pr-num.md` | PR review comments by model and PR number |
| 18 | `pr-review-comments.md` | PR review comments |
| 19 | `prompt-gemini-model.md` | Prompts Gemini model |
| 20 | `resolve-pr-comments.md` | Resolves PR review comments |

### Scripts (5 primary files)

| # | File | Purpose |
|---|------|---------|
| 1 | `devcontainer-opencode.sh` | CLI wrapper: up/start/prompt/status/stop/down commands |
| 2 | `assemble-orchestrator-prompt.sh` | Injects GitHub event data into prompt template |
| 3 | `start-opencode-server.sh` | Starts `opencode serve` as a setsid daemon |
| 4 | `resolve-image-tags.sh` | Resolves devcontainer image tag from branch and run number |
| 5 | `run_opencode_prompt.sh` | Validates API keys, exports tokens, runs opencode with watchdog |

### Config Files (3 files)

| # | File | Purpose |
|---|------|---------|
| 1 | `opencode.json` | Multi-provider model definitions, MCP servers, tool permissions |
| 2 | `AGENTS.md` | Agent instructions, project conventions, mandatory tool protocols |
| 3 | `.github/workflows/prompts/orchestrator-agent-prompt.md` | Prompt template with `__EVENT_DATA__` placeholder |

## Runtime Paths

| Path | Description | Created By |
|------|-------------|------------|
| `/tmp/opencode-serve.log` | Server log file | `start-opencode-server.sh` |
| `/tmp/opencode-serve.pid` | Server PID file | `start-opencode-server.sh` |
| `$ORCHESTRATION_ROOT/.memory/memory.jsonl` | MCP knowledge graph | `@modelcontextprotocol/server-memory` |
| `$ORCHESTRATION_ROOT/.assembled-orchestrator-prompt.md` | Assembled prompt | `assemble-orchestrator-prompt.sh` |

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ORCHESTRATION_ROOT` | `/opt/orchestration` | Root directory for all orchestration files |
| `OPENCODE_SERVER_PORT` | `4096` | Port for the opencode server |
| `OPENCODE_SERVER_HOSTNAME` | `0.0.0.0` | Hostname for the opencode server |
| `OPENCODE_SERVER_LOG` | `/tmp/opencode-serve.log` | Server log file path |
| `OPENCODE_SERVER_PIDFILE` | `/tmp/opencode-serve.pid` | Server PID file path |

## Path Resolution Strategy

All scripts resolve paths relative to `ORCHESTRATION_ROOT`:

```bash
ORCHESTRATION_ROOT="${ORCHESTRATION_ROOT:-.}"
```

- **Server container**: Set to `/opt/orchestration` via `docker-compose.yml` environment variable —
  files are baked into the image.
- **Local development**: Falls back to `.` (current directory) — scripts work from the checkout
  directory without modification.
- **GitHub Actions**: Falls back to `.` within the Actions workspace — `actions/checkout` populates
  the directory.

No symlinks are required. All paths are absolute or relative to `ORCHESTRATION_ROOT` and deterministic at runtime.
