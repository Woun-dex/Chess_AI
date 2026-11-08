"""Celery application configuration."""

from celery import Celery

from chess_ai.config import get_settings

settings = get_settings()
celery_app = Celery(
    "chess_ai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["chess_ai.infrastructure.queue.tasks"],
)
celery_app.conf.update(
    task_default_queue="analysis",
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    broker_transport_options={"visibility_timeout": 3600},
    result_expires=86400,
)
