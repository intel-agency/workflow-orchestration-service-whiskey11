"""Tests for src.config — environment variable reading, defaults, validation, and scrub_secrets."""

import importlib
import logging

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reload_config(monkeypatch: pytest.MonkeyPatch, env: dict) -> object:
    """Set env vars, reload config module, return the fresh module."""
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_ORG", raising=False)
    monkeypatch.delenv("GITHUB_REPO", raising=False)
    monkeypatch.delenv("POLL_INTERVAL", raising=False)
    monkeypatch.delenv("MAX_BACKOFF", raising=False)
    monkeypatch.delenv("WEBHOOK_PORT", raising=False)
    monkeypatch.delenv("HTTP_MAX_CONNECTIONS", raising=False)
    monkeypatch.delenv("HTTP_CONNECT_TIMEOUT", raising=False)
    monkeypatch.delenv("HTTP_READ_TIMEOUT", raising=False)

    for key, value in env.items():
        monkeypatch.setenv(key, value)

    import src.config as cfg

    importlib.reload(cfg)
    return cfg


# ---------------------------------------------------------------------------
# Default values
# ---------------------------------------------------------------------------


class TestDefaults:
    """Verify that config reads sensible defaults when env vars are unset."""

    def test_opencode_server_url_default(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {})
        assert cfg.OPENCODE_SERVER_URL == "http://127.0.0.1:4096"

    def test_opencode_server_dir_default(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {})
        assert cfg.OPENCODE_SERVER_DIR == "/opt/orchestration"

    def test_github_token_default_empty(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {})
        assert cfg.GITHUB_TOKEN == ""

    def test_poll_interval_default(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {})
        assert cfg.POLL_INTERVAL == 60
        assert isinstance(cfg.POLL_INTERVAL, int)

    def test_max_backoff_default(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {})
        assert cfg.MAX_BACKOFF == 960
        assert isinstance(cfg.MAX_BACKOFF, int)

    def test_heartbeat_interval_default(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {})
        assert cfg.HEARTBEAT_INTERVAL == 300
        assert isinstance(cfg.HEARTBEAT_INTERVAL, int)

    def test_subprocess_timeout_default(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {})
        assert cfg.SUBPROCESS_TIMEOUT == 5700
        assert isinstance(cfg.SUBPROCESS_TIMEOUT, int)

    def test_webhook_port_default(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {})
        assert cfg.WEBHOOK_PORT == 8000
        assert isinstance(cfg.WEBHOOK_PORT, int)

    def test_http_max_keepalive_default(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {})
        assert cfg.HTTP_MAX_KEEPALIVE_CONNECTIONS == 20

    def test_http_max_connections_default(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {})
        assert cfg.HTTP_MAX_CONNECTIONS == 100

    def test_http_connect_timeout_default(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {})
        assert cfg.HTTP_CONNECT_TIMEOUT == 5

    def test_http_read_timeout_default(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {})
        assert cfg.HTTP_READ_TIMEOUT == 30

    def test_log_level_default(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {})
        assert cfg.LOG_LEVEL == logging.INFO


# ---------------------------------------------------------------------------
# Environment variable overrides
# ---------------------------------------------------------------------------


class TestOverrides:
    """Verify that env vars override defaults with correct type coercion."""

    def test_github_token_from_env(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {"GITHUB_TOKEN": "FAKE-KEY-FOR-TESTING-00000000"})
        assert cfg.GITHUB_TOKEN == "FAKE-KEY-FOR-TESTING-00000000"

    def test_github_org_from_env(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {"GITHUB_ORG": "test-org"})
        assert cfg.GITHUB_ORG == "test-org"

    def test_github_repo_from_env(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {"GITHUB_REPO": "test-repo"})
        assert cfg.GITHUB_REPO == "test-repo"

    def test_poll_interval_from_env(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {"POLL_INTERVAL": "30"})
        assert cfg.POLL_INTERVAL == 30
        assert isinstance(cfg.POLL_INTERVAL, int)

    def test_webhook_port_from_env(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {"WEBHOOK_PORT": "9000"})
        assert cfg.WEBHOOK_PORT == 9000
        assert isinstance(cfg.WEBHOOK_PORT, int)

    def test_log_level_debug(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {"LOG_LEVEL": "DEBUG"})
        assert cfg.LOG_LEVEL == logging.DEBUG

    def test_log_level_warning(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {"LOG_LEVEL": "WARNING"})
        assert cfg.LOG_LEVEL == logging.WARNING

    def test_log_level_case_insensitive(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {"LOG_LEVEL": "error"})
        assert cfg.LOG_LEVEL == logging.ERROR

    def test_http_max_connections_override(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {"HTTP_MAX_CONNECTIONS": "50"})
        assert cfg.HTTP_MAX_CONNECTIONS == 50


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestValidation:
    """Verify validation behavior for invalid or missing config values."""

    def test_invalid_log_level_falls_back_to_info(self, monkeypatch):
        cfg = _reload_config(monkeypatch, {"LOG_LEVEL": "INVALID_LEVEL"})
        assert cfg.LOG_LEVEL == logging.INFO

    def test_missing_github_token_warns(self, monkeypatch, caplog):
        with caplog.at_level(logging.WARNING, logger="workflow-orchestration-client.config"):
            _reload_config(monkeypatch, {})
        assert any("GITHUB_TOKEN is not set" in record.message for record in caplog.records)

    def test_present_github_token_no_warning(self, monkeypatch, caplog):
        with caplog.at_level(logging.WARNING, logger="workflow-orchestration-client.config"):
            _reload_config(monkeypatch, {"GITHUB_TOKEN": "FAKE-KEY-FOR-TESTING-00000000"})
        token_warnings = [r for r in caplog.records if "GITHUB_TOKEN is not set" in r.message]
        assert len(token_warnings) == 0


# ---------------------------------------------------------------------------
# scrub_secrets re-export
# ---------------------------------------------------------------------------


class TestScrubSecretsReExport:
    """Verify scrub_secrets is importable from config module."""

    def test_scrub_secrets_available(self):
        from src.config import scrub_secrets

        assert callable(scrub_secrets)

    def test_scrub_secrets_works(self):
        from src.config import scrub_secrets

        result = scrub_secrets("hello world")
        assert result == "hello world"

    def test_scrub_secrets_redacts_synthetic_key(self):
        """Use obviously synthetic values that won't trigger gitleaks."""
        from src.config import scrub_secrets

        # This matches the Bearer pattern
        text = "Authorization: Bearer FAKE-BEARER-TOKEN-FOR-TESTING-ONLY-12345678901234567890=="
        result = scrub_secrets(text)
        assert "***REDACTED***" in result
        assert "FAKE-BEARER-TOKEN" not in result
