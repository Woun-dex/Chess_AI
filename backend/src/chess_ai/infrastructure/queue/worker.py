"""Celery worker entrypoint."""

from chess_ai.infrastructure.queue.celery_app import celery_app

__all__ = ["celery_app"]


if __name__ == "__main__":
    celery_app.worker_main(["worker", "--loglevel=INFO", "--concurrency=2", "--queues=analysis"])
