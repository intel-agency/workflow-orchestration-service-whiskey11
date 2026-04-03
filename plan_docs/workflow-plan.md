# Workflow Execution Plan: project-setup

**Generated:** 2026-04-03
**Workflow:** `dynamic-workflows/project-setup.md`
**Repository:** `intel-agency/workflow-orchestration-service-whiskey11`

---

## 1. Overview

This document is the workflow execution plan for the `project-setup` dynamic workflow, which orchestrates the initial setup of the **Workflow Orchestration Service** repository — a standalone client/server orchestration service migrating from a GitHub Actions-embedded model.

**Project:** Workflow Orchestration Service — Standalone Orchestration Service Migration
**Description:** Migrate the orchestration workflow agent from a GitHub Actions-embedded model to a standalone, self-hosted, networked client/server service. The server runs the full orchestration stack (opencode CLI, agents, MCP servers) inside a Docker image. The client is a Python service that receives GitHub events via webhooks and dispatches prompts to the remote server.

**Total assignments:** 6 main + 1 pre-script + 2 post-assignment events + 1 post-script event
**High-level summary:** Initialize the repository, create an application plan, set up the project structure, configure agent documentation, debrief, and merge all changes via PR.

---

## 2. Project Context Summary

### Key Facts

| Attribute | Value |
|-----------|-------|
| Repository | `intel-agency/workflow-orchestration-service-whiskey11` |
| Language | Python 3.12+ |
| Framework | FastAPI, httpx, Pydantic, uvicorn |
| Package Manager | uv (Astral) |
| Containerization | Docker, Docker Compose |
| Build/CI | GitHub Actions (validate.yml) |
| Validation | `pwsh -NoProfile -File ./scripts/validate.ps1 -All` |
| Agent Runtime | opencode CLI (v1.2.24) |
| Architecture | Client/Server — Server (opencode serve, Docker, :4096) + Client (FastAPI webhook handler + Sentinel polling, :8000) |
| Existing Code Coverage | ~80-95% for core components (Sentinel, Notifier, WorkItem model, GitHub Queue) |
| Primary Effort | Integration and packaging — not greenfield development |

### Technology Stack

- **Python 3.12+** — Sentinel, Webhook Notifier, models, queue
- **FastAPI** — Webhook handler (async, Pydantic, auto-OpenAPI)
- **Pydantic** — Data schemas (WorkItem, TaskType, WorkItemStatus)
- **httpx** — Async HTTP client for GitHub API
- **uvicorn** — ASGI server
- **uv** — Python package manager (Rust-based, fast)
- **Bash/PowerShell** — Shell bridge scripts, auth, validation
- **Docker** — Server container, client container, compose

### Plan Documents

| Document | Path | Purpose |
|----------|------|---------|
| Application Implementation Specification v1.2 | `plan_docs/Application Implementation Specification - workflow-orchestration-service v1.2.md` | Detailed spec with 6 phases, 29 tasks, agent assignments, risk register |
| Migration & Implementation Plan | `plan_docs/Standalone Service Migration Plan - workflow-orchestration-service.md` | Full 6-phase migration plan with architecture, code inventory, validation plans |
| Sentinel Orchestrator | `plan_docs/src/orchestrator_sentinel.py` | Polling, claiming, heartbeats, shell bridge (~90% complete) |
| Webhook Notifier | `plan_docs/src/notifier_service.py` | FastAPI, HMAC verification, event triage (~80% complete) |
| Work Item Model | `plan_docs/src/models/work_item.py` | Pydantic models, credential scrubbing (~95% complete) |
| GitHub Queue | `plan_docs/src/queue/github_queue.py` | ITaskQueue, claim, heartbeat, status updates (~85% complete) |

### Key Constraints

- Action SHA pinning is mandatory for all GitHub Actions workflows
- All validation must pass before commits (`./scripts/validate.ps1 -All`)
- Feature branch + PR path for code changes (no direct pushes to main)
- No secrets in code; use environment variables
- Shell bridge (`devcontainer-opencode.sh`) is the primary API for Sentinel ↔ Server communication

---

## 3. Assignment Execution Plan

### 3.1 Pre-script-begin: `create-workflow-plan`

| Field | Content |
|-------|---------|
| **Assignment** | `create-workflow-plan`: Create Workflow Plan |
| **Goal** | Create a comprehensive workflow execution plan documenting how each assignment will be executed |
| **Key Acceptance Criteria** | Dynamic workflow fully read; all assignments traced; all plan_docs read; plan produced and approved; committed as `plan_docs/workflow-plan.md` |
| **Project-Specific Notes** | Plan docs contain detailed implementation spec with 6 phases and 29 tasks. This is primarily an integration/packaging effort with substantial existing code. |
| **Prerequisites** | None (first assignment) |
| **Dependencies** | None |
| **Risks / Challenges** | Plan docs are very detailed — need to distill into actionable workflow steps |
| **Events** | None |

### 3.2 `init-existing-repository`

| Field | Content |
|-------|---------|
| **Assignment** | `init-existing-repository`: Initiate Existing Repository |
| **Goal** | Initialize the existing repository by creating a feature branch, importing branch protection rules, creating a GitHub Project, importing labels, renaming workspace/devcontainer files, and creating a PR |
| **Key Acceptance Criteria** | (0) New branch created first; (1) Branch protection ruleset imported; (2) GitHub Project created; (3) Project linked to repo; (4) Project columns created; (5) Labels imported; (6) Filenames changed to match project; (7) PR created |
| **Project-Specific Notes** | Repo already has `.github/.labels.json` and `.github/protected-branches_ruleset.json`. The repo name is `workflow-orchestration-service-whiskey11`. Workspace files may already be named correctly. |
| **Prerequisites** | GitHub authentication with `repo`, `project`, `read:project`, `read:user`, `user:email`, `administration:write` scopes |
| **Dependencies** | Pre-script event (create-workflow-plan) must complete |
| **Risks / Challenges** | Branch protection import requires `administration:write` scope; PAT must be `GH_ORCHESTRATION_AGENT_TOKEN`. Workspace files may already have correct names. |
| **Events** | Post-assignment: `validate-assignment-completion`, `report-progress` |

### 3.3 `create-app-plan`

| Field | Content |
|-------|---------|
| **Assignment** | `create-app-plan`: Create Application Plan |
| **Goal** | Create a comprehensive application plan based on the plan docs, documented as a GitHub Issue |
| **Key Acceptance Criteria** | Template analyzed; project structure documented; plan uses Appendix A template; detailed phase breakdown; all requirements addressed; risks and mitigations identified; plan documented in an issue; milestones created; issue added to GitHub Project; issue assigned to milestone; labels applied |
| **Project-Specific Notes** | Plan docs already contain very detailed implementation specs (Application Implementation Specification v1.2 and Migration Plan). The plan should synthesize these into an actionable issue. Tech stack: Python/FastAPI. This is PLANNING ONLY — no code. |
| **Prerequisites** | Repository initialized; labels imported; GitHub Project created |
| **Dependencies** | `init-existing-repository` (labels, project, milestones must exist) |
| **Risks / Challenges** | Plan docs are very detailed — the issue plan needs to be a practical summary, not a copy. Application plan template (Appendix A) is in `.github/ISSUE_TEMPLATE/application-plan.md`. |
| **Events** | Pre-assignment: `gather-context`; On-failure: `recover-from-error`; Post-assignment (internal): `report-progress`; Post-assignment (workflow): `validate-assignment-completion`, `report-progress` |

### 3.4 `create-project-structure`

| Field | Content |
|-------|---------|
| **Assignment** | `create-project-structure`: Create Project Structure |
| **Goal** | Create the actual project structure and scaffolding based on the application plan |
| **Key Acceptance Criteria** | Solution/project structure created; all required files/directories established; configuration files created; CI/CD pipeline structure established; documentation structure created; dev environment validated; initial commit made; stakeholder approval obtained; repository summary created; all GitHub Actions pinned to SHAs |
| **Project-Specific Notes** | Tech stack is Python/uv (not .NET). Use `pyproject.toml` for project metadata, `uv` for package management. Existing code in `plan_docs/src/` should be integrated into the project structure. Key directories: `client/src/` (FastAPI service), `server/` (Dockerfile, scripts), shared models/queue modules. |
| **Prerequisites** | Application plan approved and documented |
| **Dependencies** | `create-app-plan` (application plan issue and tech-stack.md, architecture.md) |
| **Risks / Challenges** | Must follow Python/uv conventions, not .NET. Existing code in plan_docs needs to be moved, not duplicated. Dockerfile for server is in external repo — only client Dockerfile needed here. |
| **Events** | Post-assignment: `validate-assignment-completion`, `report-progress` |

### 3.5 `create-agents-md-file`

| Field | Content |
|-------|---------|
| **Assignment** | `create-agents-md-file`: Create AGENTS.md File |
| **Goal** | Create a comprehensive `AGENTS.md` file at the repository root for AI coding agents |
| **Key Acceptance Criteria** | File exists at root; contains project overview, setup/build/test commands (verified), code style, project structure, testing instructions, PR/commit guidelines; commands validated; committed and pushed; stakeholder approval |
| **Project-Specific Notes** | An `AGENTS.md` already exists at the root (template version). It needs to be updated with project-specific content for the orchestration service. Must reflect the Python/FastAPI tech stack, not the generic template content. |
| **Prerequisites** | Project structure created |
| **Dependencies** | `create-project-structure` (project structure, build commands, tech stack) |
| **Risks / Challenges** | Existing AGENTS.md has template content that must be replaced, not just appended to. Commands must be verified to work. |
| **Events** | Post-assignment: `validate-assignment-completion`, `report-progress` |

### 3.6 `debrief-and-document`

| Field | Content |
|-------|---------|
| **Assignment** | `debrief-and-document`: Debrief and Document Learnings |
| **Goal** | Perform a comprehensive debriefing capturing lessons learned, successes, and gaps |
| **Key Acceptance Criteria** | Detailed report created using structured template (12 sections); all deviations documented; report reviewed and approved; committed and pushed; execution trace saved |
| **Project-Specific Notes** | This debrief should capture the unique aspects of this project (integration vs. greenfield, Python/FastAPI stack, existing code at 80-95% coverage, Docker-based architecture). |
| **Prerequisites** | All previous assignments completed |
| **Dependencies** | All prior main assignments |
| **Risks / Challenges** | Need thorough execution trace of all actions taken |
| **Events** | Post-assignment: `validate-assignment-completion`, `report-progress` |

### 3.7 `pr-approval-and-merge`

| Field | Content |
|-------|---------|
| **Assignment** | `pr-approval-and-merge`: PR Approval and Merge |
| **Goal** | Complete the full PR approval and merge process for the setup PR |
| **Key Acceptance Criteria** | CI checks pass (with up to 3 remediation attempts); code review delegated; review comments resolved; approval obtained; merge performed; source branch deleted; related issues closed |
| **Project-Specific Notes** | PR number comes from `init-existing-repository` output. This is an automated setup PR — self-approval is acceptable per workflow instructions. CI remediation loop is mandatory. Setup branch should be deleted after merge. |
| **Prerequisites** | All work committed to the feature branch; PR already created |
| **Dependencies** | `init-existing-repository` (PR number), all other assignments (all changes committed) |
| **Risks / Challenges** | CI may have lint/test failures from new project files. Must run `./scripts/validate.ps1 -All` before merge. Must handle branch protection rules. |
| **Events** | Post-assignment: `validate-assignment-completion`, `report-progress` |

### 3.8 Post-script-complete: Apply `orchestration:plan-approved` Label

| Field | Content |
|-------|---------|
| **Action** | Apply `orchestration:plan-approved` label to the plan issue from `create-app-plan` |
| **Goal** | Signal that the plan is ready for epic creation, triggering the next orchestration phase |
| **Key Acceptance Criteria** | Label applied to the correct plan issue |
| **Dependencies** | `create-app-plan` (plan issue number), all assignments complete |

---

## 4. Sequencing Diagram

```
pre-script-begin
└── create-workflow-plan → plan_docs/workflow-plan.md
        │
        ▼
init-existing-repository → branch + PR
│   └── post: validate-assignment-completion + report-progress
│
├── create-app-plan → plan issue + milestones
│   └── post: validate-assignment-completion + report-progress
│
├── create-project-structure → project scaffolding
│   └── post: validate-assignment-completion + report-progress
│
├── create-agents-md-file → AGENTS.md
│   └── post: validate-assignment-completion + report-progress
│
├── debrief-and-document → debrief report
│   └── post: validate-assignment-completion + report-progress
│
└── pr-approval-and-merge → merged PR, closed branch
    └── post: validate-assignment-completion + report-progress
        │
        ▼
post-script-complete
└── Apply orchestration:plan-approved label to plan issue
```

---

## 5. Open Questions

1. **Existing AGENTS.md**: The repository already has an `AGENTS.md` at the root (template version). Should this be replaced entirely or merged with project-specific content? → **Resolution**: Replace with project-specific content per `create-agents-md-file` assignment.

2. **Application plan template**: The `create-app-plan` assignment references Appendix A template located at `.github/ISSUE_TEMPLATE/application-plan.md`. Need to verify this file exists or adapt accordingly.

3. **Existing code in plan_docs/src/**: The plan docs contain substantial Python code (Sentinel, Notifier, WorkItem, GitHub Queue). Should `create-project-structure` move this code into the project structure or leave it as reference? → **Resolution**: Per the implementation spec, these modules should be copied and adapted into the client project structure.

4. **Branch naming**: The `init-existing-repository` assignment specifies branch name should be `dynamic-workflow-project-setup`. This aligns with the dynamic workflow name.

5. **Labels**: Need to verify `.github/.labels.json` contains the required labels including `orchestration:plan-approved` for the post-script-complete event.
