import os
from core.config import settings

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celery application configuration object
CELERY_CONFIG = {
    "broker_url": REDIS_URL,
    "result_backend": REDIS_URL,
    "task_serializer": "json",
    "result_serializer": "json",
    "accept_content": ["json"],
    "timezone": "UTC",
    "enable_utc": True,
    "task_track_started": True,
    "task_time_limit": 600,       # 10 minutes max per task
    "task_soft_time_limit": 540,  # 9 minutes soft limit
    "task_routes": {
        "workers.tasks.sync_jobs_task": {"queue": "sync_jobs_queue"},
        "workers.tasks.calculate_matching_task": {"queue": "matching_queue"},
        "workers.tasks.generate_report_task": {"queue": "reports_queue"},
    },
    "worker_prefetch_multiplier": 1,
    "worker_concurrency": int(os.getenv("WORKER_CONCURRENCY", "4")),
}

try:
    from celery import Celery
    celery_app = Celery("job_copilot_worker")
    celery_app.conf.update(CELERY_CONFIG)
except ImportError:
    celery_app = None
