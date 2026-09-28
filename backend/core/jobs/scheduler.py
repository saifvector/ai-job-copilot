import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from core.database import AsyncSessionFactory
from services.job_service import JobService

logger = logging.getLogger("core.jobs.scheduler")

# Background scheduler instance
scheduler = AsyncIOScheduler()


async def scheduled_job_sync_task() -> None:
    """
    Scheduled job sync task running every 6 hours across all registered providers.
    """
    logger.info("Executing periodic 6-hour job synchronization task...")
    try:
        async with AsyncSessionFactory() as session:
            service = JobService(session)

            result = await service.sync_jobs()
            logger.info(f"Periodic job sync completed: {result.message}")
    except Exception as exc:
        logger.error(f"Error during periodic job sync task: {exc}", exc_info=True)


def start_job_scheduler() -> None:
    """
    Initializes and starts the APScheduler background runner.
    Default interval: every 6 hours (configurable via SYNC_INTERVAL_HOURS env).
    """
    if os.getenv("DISABLE_BACKGROUND_SCHEDULER", "false").lower() == "true":
        logger.info("Background job scheduler is disabled via environment variable.")
        return

    interval_hours = int(os.getenv("SYNC_INTERVAL_HOURS", "6"))

    if not scheduler.running:
        scheduler.add_job(
            scheduled_job_sync_task,
            trigger=IntervalTrigger(hours=interval_hours),
            id="periodic_job_sync",
            name="Periodic Job Sync Task (6 hours)",
            replace_existing=True,
        )
        scheduler.start()
        logger.info(f"Job Discovery Engine background scheduler started (Interval: {interval_hours} hours).")


def stop_job_scheduler() -> None:
    """
    Gracefully halts the background scheduler during application shutdown.
    """
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Job Discovery Engine background scheduler stopped.")
