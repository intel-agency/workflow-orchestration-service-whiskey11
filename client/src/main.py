"""Entry point for the workflow-orchestration-client.

Supports dual-mode operation:
- Webhook mode: FastAPI server receives GitHub events
- Polling mode: Sentinel polls for queued issues
Both modes run concurrently.
"""

import asyncio
import uvicorn
from src.config import WEBHOOK_PORT


async def main():
    """Run webhook server and sentinel polling loop concurrently."""
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
    asyncio.run(main())
