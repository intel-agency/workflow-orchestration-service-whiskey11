"""Centralized configuration for the workflow-orchestration-client.

All settings are read from environment variables with sensible defaults.
No pydantic-settings — keeps it simple with os.environ for Phase 1.
"""

import logging
import os

from src.models.work_item import scrub_secrets  # noqa: F401 — re-exported for convenience

logger = logging.getLogger("workflow-orchestration-client.config")


def _safe_int(value: str | None, default: int) -> int:
    """Safely parse an integer from an env var, returning default on failure."""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# --- Logging ---
# LOG_LEVEL: Controls the verbosity of application logging.
# Accepts standard Python logging level names (DEBUG, INFO, WARNING, ERROR, CRITICAL).
# Default: "INFO"
_LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
try:
    _level_value = logging.getLevelName(_LOG_LEVEL_STR)
    if not isinstance(_level_value, int):
        raise ValueError(f"Invalid log level: {_LOG_LEVEL_STR}")
    LOG_LEVEL: int = _level_value
except (ValueError, TypeError):
    logger.warning("LOG_LEVEL '%s' is invalid; falling back to INFO", _LOG_LEVEL_STR)
    LOG_LEVEL = logging.INFO

# --- Server Connection ---
# OPENCODE_SERVER_URL: Base URL of the opencode server for agent dispatch.
# Default: "http://127.0.0.1:4096"
OPENCODE_SERVER_URL: str = os.getenv("OPENCODE_SERVER_URL", "http://127.0.0.1:4096")

# OPENCODE_SERVER_DIR: Working directory inside the opencode server container.
# Default: "/opt/orchestration"
OPENCODE_SERVER_DIR: str = os.getenv("OPENCODE_SERVER_DIR", "/opt/orchestration")

# --- GitHub ---
# GITHUB_TOKEN: Personal access token for GitHub API operations.
# Required for sentinel polling and queue operations. Empty string if not set.
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")

# GITHUB_ORG: GitHub organization name for sentinel polling.
# Default: "" (must be set for sentinel mode)
GITHUB_ORG: str = os.getenv("GITHUB_ORG", "")

# GITHUB_REPO: GitHub repository name (without org prefix) for sentinel polling.
# Default: "" (must be set for sentinel mode)
GITHUB_REPO: str = os.getenv("GITHUB_REPO", "")

# Log warning for missing GITHUB_TOKEN at import time.
# Does NOT exit — sentinel/notifier will handle the error with proper context.
if not GITHUB_TOKEN:
    logger.warning(
        "GITHUB_TOKEN is not set. Sentinel polling and GitHub API operations will fail. "
        "Set GITHUB_TOKEN environment variable to resolve."
    )

# --- Sentinel ---
# SENTINEL_BOT_LOGIN: GitHub login of the bot account for assign-then-verify locking.
# Default: "" (locking disabled when empty)
SENTINEL_BOT_LOGIN: str = os.getenv("SENTINEL_BOT_LOGIN", "")

# POLL_INTERVAL: Seconds between sentinel polling cycles.
# Default: 60
POLL_INTERVAL: int = _safe_int(os.getenv("POLL_INTERVAL"), 60)

# MAX_BACKOFF: Maximum seconds for exponential backoff on rate limits.
# Default: 960 (16 minutes)
MAX_BACKOFF: int = _safe_int(os.getenv("MAX_BACKOFF"), 960)

# HEARTBEAT_INTERVAL: Seconds between heartbeat comments during task execution.
# Default: 300 (5 minutes)
HEARTBEAT_INTERVAL: int = _safe_int(os.getenv("HEARTBEAT_INTERVAL"), 300)

# SUBPROCESS_TIMEOUT: Hard timeout in seconds for subprocess execution.
# Default: 5700 (95 minutes) — higher than inner watchdog ceiling (5400s)
SUBPROCESS_TIMEOUT: int = _safe_int(os.getenv("SUBPROCESS_TIMEOUT"), 5700)

# --- Webhook ---
# WEBHOOK_SECRET: Secret key for verifying GitHub webhook signatures.
# Default: "" (must be set for webhook mode)
WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")

# WEBHOOK_PORT: Port for the FastAPI webhook server.
# Default: 8000
WEBHOOK_PORT: int = _safe_int(os.getenv("WEBHOOK_PORT"), 8000)

# --- Shell Bridge ---
# SHELL_BRIDGE_PATH: Path to the devcontainer-opencode.sh shell bridge script.
# Default: ../scripts/devcontainer-opencode.sh relative to this file
SHELL_BRIDGE_PATH: str = os.getenv(
    "SHELL_BRIDGE_PATH",
    os.path.join(os.path.dirname(__file__), "..", "scripts", "devcontainer-opencode.sh"),
)

# --- HTTP Client ---
# HTTP_MAX_KEEPALIVE_CONNECTIONS: Maximum number of keep-alive connections in the pool.
# Default: 20
HTTP_MAX_KEEPALIVE_CONNECTIONS: int = _safe_int(os.getenv("HTTP_MAX_KEEPALIVE_CONNECTIONS"), 20)

# HTTP_MAX_CONNECTIONS: Maximum total connections in the pool.
# Default: 100
HTTP_MAX_CONNECTIONS: int = _safe_int(os.getenv("HTTP_MAX_CONNECTIONS"), 100)

# HTTP_CONNECT_TIMEOUT: Connection timeout in seconds.
# Default: 5
HTTP_CONNECT_TIMEOUT: int = _safe_int(os.getenv("HTTP_CONNECT_TIMEOUT"), 5)

# HTTP_READ_TIMEOUT: Read timeout in seconds.
# Default: 30
HTTP_READ_TIMEOUT: int = _safe_int(os.getenv("HTTP_READ_TIMEOUT"), 30)

# HTTP_WRITE_TIMEOUT: Write timeout in seconds.
# Default: 30
HTTP_WRITE_TIMEOUT: int = _safe_int(os.getenv("HTTP_WRITE_TIMEOUT"), 30)

# HTTP_POOL_TIMEOUT: Pool timeout (waiting for a connection) in seconds.
# Default: 10
HTTP_POOL_TIMEOUT: int = _safe_int(os.getenv("HTTP_POOL_TIMEOUT"), 10)
