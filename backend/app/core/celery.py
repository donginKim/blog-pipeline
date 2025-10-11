# Celery configuration
from celery import Celery
from .core.config import settings

# Create Celery app
celery_app = Celery(
    "naver_monitor",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.workers.crawl_worker",
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Optional: Configure periodic tasks
celery_app.conf.beat_schedule = {
    "crawl-all-keywords": {
        "task": "app.workers.crawl_worker.crawl_all_keywords_task",
        "schedule": 3600.0,  # Run every hour
    },
}

celery_app.conf.timezone = "Asia/Seoul"

