from celery import Celery

from app.core.config import settings

celery_client = Celery(
    "echocheck_api",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


def enqueue_geo_run(run_id: str) -> None:
    celery_client.send_task("geo.process_run", args=[run_id])
