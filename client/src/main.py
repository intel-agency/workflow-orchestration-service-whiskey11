"""Entry point for the workflow-orchestration-client.

Supports dual-mode operation:
- Webhook mode: FastAPI server receives GitHub events
- Polling mode: Sentinel polls for queued issues
Both modes run concurrently.

Also provides a `create_app()` factory for testing and standalone webhook mode,
with lifespan-managed httpx client, CORS middleware, and health endpoint.
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import (
    WEBHOOK_PORT,
    HTTP_MAX_KEEPALIVE_CONNECTIONS,
    HTTP_MAX_CONNECTIONS,
    HTTP_CONNECT_TIMEOUT,
    HTTP_READ_TIMEOUT,
    HTTP_WRITE_TIMEOUT,
    HTTP_POOL_TIMEOUT,
)

logger = logging.getLogger("workflow-orchestration-client")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage the shared httpx client lifecycle.

    Creates an AsyncClient with connection pool limits and timeout defaults
    on startup, stores it on app.state.http_client, and closes it on shutdown.
    """
    # Create shared httpx client with pool limits and timeouts
    client = httpx.AsyncClient(
        limits=httpx.Limits(
            max_keepalive_connections=HTTP_MAX_KEEPALIVE_CONNECTIONS,
            max_connections=HTTP_MAX_CONNECTIONS,
        ),
        timeout=httpx.Timeout(
            connect=HTTP_CONNECT_TIMEOUT,
            read=HTTP_READ_TIMEOUT,
            write=HTTP_WRITE_TIMEOUT,
            pool=HTTP_POOL_TIMEOUT,
        ),
    )
    app.state.http_client = client
    logger.info("Application startup complete — httpx client initialized")
    yield
    # Shutdown: close the httpx client
    await client.aclose()
    logger.info("Application shutdown complete — httpx client closed")


def create_app() -> FastAPI:
    """Create and configure a FastAPI application instance.

    Returns a configured FastAPI app with:
    - Lifespan-managed httpx.AsyncClient (accessible via app.state.http_client)
    - CORS middleware for cross-origin requests
    - GET /health endpoint for health checks

    This factory is intended for testing and standalone webhook mode.
    For the dual-mode runner (webhook + sentinel polling), use main() instead.
    """
    app = FastAPI(
        title="Workflow Orchestration Client",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware — wildcard origins (restrict in production)
    # NOTE: allow_credentials=True is incompatible with allow_origins=["*"]
    # and would cause a runtime CORS error. Remove credentials if using wildcards.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health_check() -> dict:
        """Health check endpoint for monitoring and load balancers."""
        return {"status": "online", "system": "workflow-orchestration-client"}

    return app


async def main():
    """Run webhook server and sentinel polling loop concurrently.

    This is the primary entry point for the dual-mode orchestration client.
    It imports the notifier's FastAPI app and the Sentinel orchestrator,
    then runs both concurrently.
    """
    # Import here to avoid circular imports and allow config loading first
    from src.notifier import app  # noqa: F401
    from src.sentinel import Sentinel
    from src.queue.github_queue import GitHubQueue
    from src.config import GITHUB_TOKEN, GITHUB_ORG, GITHUB_REPO

    queue = GitHubQueue(GITHUB_TOKEN, GITHUB_ORG, GITHUB_REPO)
    sentinel = Sentinel(queue)

    server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=WEBHOOK_PORT))

    try:
        await asyncio.gather(
            server.serve(),
            sentinel.run_forever(),
        )
    finally:
        await queue.close()


if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=WEBHOOK_PORT)
