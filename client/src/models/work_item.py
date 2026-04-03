"""
workflow-orchestration-service Unified Work Item Model

Canonical data model shared by both the Sentinel Orchestrator and the
Work Event Notifier. Both components import from this module to prevent
model divergence.

See: workflow-orchestration-service Plan Review, I-1 / R-3
"""

import re
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """The kind of work the agent should perform."""

    PLAN = "PLAN"
    IMPLEMENT = "IMPLEMENT"
    BUGFIX = "BUGFIX"
    PULL_REQUEST = "PULL_REQUEST"
    REVIEW = "REVIEW"
    WORKFLOW_DISPATCH = "WORKFLOW_DISPATCH"
    OTHER = "OTHER"


class WorkItemStatus(str, Enum):
    """Maps directly to GitHub Issue labels used as state indicators.

    Includes both GitHub label-based values (used by sentinel/notifier)
    and generic lifecycle values for cross-provider usage.
    """

    # GitHub label-based statuses (used by sentinel and notifier)
    QUEUED = "agent:queued"
    IN_PROGRESS = "agent:in-progress"
    RECONCILING = "agent:reconciling"
    SUCCESS = "agent:success"
    ERROR = "agent:error"
    INFRA_FAILURE = "agent:infra-failure"
    STALLED_BUDGET = "agent:stalled-budget"

    # Generic lifecycle statuses (provider-agnostic)
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class WorkItem(BaseModel):
    """Unified work item used across all workflow-orchestration-service components.

    Fields populated by the Notifier are marked Optional so the Sentinel
    can construct WorkItems from its own polling results without requiring
    the raw webhook payload.

    Extended fields (title, body, repository, labels, assignees, etc.)
    are all Optional with defaults to maintain backward compatibility.
    """

    model_config = {"from_attributes": True}

    # --- Core fields (required) ---
    id: str
    issue_number: int
    source_url: str
    context_body: str
    target_repo_slug: str
    task_type: TaskType
    status: WorkItemStatus
    node_id: str

    # --- Extended fields (all optional with defaults) ---
    title: Optional[str] = Field(default=None, description="Issue or task title")
    body: Optional[str] = Field(default=None, description="Full body/description of the work item")
    repository: Optional[str] = Field(default=None, description="Repository full name (org/repo)")
    labels: List[str] = Field(default_factory=list, description="List of label names")
    assignees: List[str] = Field(default_factory=list, description="List of assignee login names")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    metadata: Dict[str, object] = Field(default_factory=dict, description="Arbitrary metadata for extensibility")


# --- Credential Scrubber (R-7) ---
# Regex patterns that match common secret formats. Used to sanitize
# worker output before posting to GitHub issue comments.

_SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9_]{36,}"),  # GitHub PAT (classic)
    re.compile(r"ghs_[A-Za-z0-9_]{36,}"),  # GitHub App installation token
    re.compile(r"gho_[A-Za-z0-9_]{36,}"),  # GitHub OAuth token
    re.compile(r"github_pat_[A-Za-z0-9_]{22,}"),  # GitHub fine-grained PAT
    re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),
    re.compile(r"token\s+[A-Za-z0-9\-._~+/]{20,}", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),  # OpenAI-style API keys
    re.compile(r"[A-Za-z0-9]{32,}\.zhipu[A-Za-z0-9]*"),  # ZhipuAI keys
]


def scrub_secrets(text: str, replacement: str = "***REDACTED***") -> str:
    """Strip known secret patterns from text for safe public posting.

    Args:
        text: The input string potentially containing secrets.
        replacement: The string to replace matched secrets with.

    Returns:
        The sanitized string with secrets replaced.
    """
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text
