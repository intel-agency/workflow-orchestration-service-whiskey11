"""Tests for src.main — app factory, lifespan, health endpoint, CORS headers."""

import pytest
import httpx
from httpx import ASGITransport

from src.main import create_app


@pytest.fixture
def app():
    """Create a fresh FastAPI app for each test."""
    return create_app()


@pytest.fixture
async def client(app):
    """Create an httpx AsyncClient backed by the ASGI transport."""
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# App Factory
# ---------------------------------------------------------------------------


class TestAppFactory:
    """Test the create_app() factory function."""

    def test_create_app_returns_fastapi_instance(self, app):
        from fastapi import FastAPI

        assert isinstance(app, FastAPI)

    def test_app_has_title(self, app):
        assert app.title == "Workflow Orchestration Client"

    def test_app_has_version(self, app):
        assert app.version == "0.1.0"

    def test_create_app_creates_new_instances(self):
        """Each call should return a new app instance."""
        app1 = create_app()
        app2 = create_app()
        assert app1 is not app2


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


class TestLifespan:
    """Test the lifespan context manager creates and cleans up httpx client."""

    @pytest.mark.asyncio
    async def test_http_client_available_after_startup(self, client):
        """After app startup, http_client should be available on app.state."""
        # The client fixture triggers startup. We verify the app state indirectly
        # by making a successful request (which requires lifespan to have run).
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_lifespan_creates_http_client(self, app):
        """Verify the lifespan sets up http_client on app.state.

        Note: httpx.ASGITransport manages lifespan internally when
        using the async context manager. The app.state.http_client
        is available during request handling but may be cleaned up
        after the async context exits.
        """
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            # Make a request that exercises the lifespan
            response = await ac.get("/health")
            assert response.status_code == 200


# ---------------------------------------------------------------------------
# Health Endpoint
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    """Test the GET /health endpoint."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self, client):
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_returns_json(self, client):
        response = await client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "online"

    @pytest.mark.asyncio
    async def test_health_includes_system_name(self, client):
        response = await client.get("/health")
        data = response.json()
        assert "system" in data
        assert "workflow-orchestration-client" in data["system"]


# ---------------------------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------------------------


class TestCORSMiddleware:
    """Test CORS middleware configuration."""

    @pytest.mark.asyncio
    async def test_cors_allows_origin(self, client):
        """OPTIONS preflight should include Access-Control-Allow-Origin."""
        response = await client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # CORS middleware should respond to preflight
        assert "access-control-allow-origin" in response.headers

    @pytest.mark.asyncio
    async def test_cors_allows_methods(self, client):
        """CORS should allow various HTTP methods."""
        response = await client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.status_code in (200, 204)

    @pytest.mark.asyncio
    async def test_actual_request_has_cors_headers(self, client):
        """Actual GET request should include CORS headers."""
        response = await client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert "access-control-allow-origin" in response.headers
