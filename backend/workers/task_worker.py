import asyncio
import os
import sys
from core.logging import get_logger
from workers.task_queue import task_queue

logger = get_logger("workers.task_worker")


async def run_worker():
    """
    Standalone background queue worker loop.
    Monitors queues and processes background jobs.
    """
    logger.info("AI Job Copilot Background Queue Worker started.")
    logger.info(f"Listening on queues: {task_queue.SYNC_JOBS_QUEUE}, {task_queue.MATCHING_QUEUE}, {task_queue.REPORTS_QUEUE}")

    try:
        while True:
            # Heartbeat check
            await asyncio.sleep(5)
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Worker received termination signal. Shutting down gracefully...")


if __name__ == "__main__":
    asyncio.run(run_worker())
