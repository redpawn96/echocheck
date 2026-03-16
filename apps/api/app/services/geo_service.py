import logging
import json
from datetime import UTC, datetime
from datetime import time as dt_time

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.api.routes_workspaces import assert_workspace_owner
from app.core.celery_client import enqueue_geo_run
from app.db.models import Brand, GeoRun, Subscription, UsageEvent
from app.schemas.geo import GeoRunRequest, GeoRunResponse, GeoRunStatusResponse

logger = logging.getLogger(__name__)


def _month_window_utc() -> tuple[datetime, datetime]:
    now = datetime.now(UTC)
    month_start = datetime.combine(now.date().replace(day=1), dt_time.min)
    if now.month == 12:
        next_month_start = datetime(year=now.year + 1, month=1, day=1)
    else:
        next_month_start = datetime(year=now.year, month=now.month + 1, day=1)
    return month_start, next_month_start


def _require_quota_capacity(db: Session, workspace_id: str) -> tuple[Subscription, int]:
    subscription = db.scalar(select(Subscription).where(Subscription.workspace_id == workspace_id))
    if subscription is None or subscription.status != "active":
        logger.info("geo_run_rejected_no_active_subscription workspace_id=%s", workspace_id)
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Active subscription required")

    monthly_quota = max(subscription.monthly_quota, 0)
    month_start, next_month_start = _month_window_utc()

    used = db.scalar(
        select(func.coalesce(func.sum(UsageEvent.units), 0)).where(
            and_(
                UsageEvent.workspace_id == workspace_id,
                UsageEvent.event_type == "geo_run_queued",
                UsageEvent.created_at >= month_start,
                UsageEvent.created_at < next_month_start,
            )
        )
    )
    used_units = int(used or 0)

    if used_units >= monthly_quota:
        logger.info(
            "geo_run_rejected_quota_exceeded workspace_id=%s used=%s quota=%s",
            workspace_id,
            used_units,
            monthly_quota,
        )
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Monthly quota exceeded")

    return subscription, used_units


def queue_geo_run(db: Session, payload: GeoRunRequest) -> GeoRunResponse:
    brand = db.get(Brand, payload.brand_id)
    if brand is None or brand.workspace_id != payload.workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found in workspace")

    _require_quota_capacity(db, payload.workspace_id)

    run = GeoRun(
        workspace_id=payload.workspace_id,
        brand_id=payload.brand_id,
        status="queued",
        providers_csv=",".join(payload.providers),
        intents_csv="\n".join(payload.intents),
    )
    db.add(run)
    db.flush()

    db.add(
        UsageEvent(
            workspace_id=payload.workspace_id,
            event_type="geo_run_queued",
            units=1,
            metadata_json=json.dumps({"runId": run.id, "brandId": payload.brand_id}),
        )
    )

    db.commit()
    db.refresh(run)
    logger.info("usage_event_recorded workspace_id=%s event_type=geo_run_queued run_id=%s", payload.workspace_id, run.id)

    try:
        enqueue_geo_run(run.id)
    except Exception as exc:  # noqa: BLE001
        # Keep the API request successful even if broker is temporarily unavailable.
        logger.warning("Failed to enqueue GEO run %s: %s", run.id, exc)

    return GeoRunResponse(runId=run.id, status=run.status)


def get_geo_run_status(db: Session, run_id: str, user_id: str) -> GeoRunStatusResponse:
    run = db.get(GeoRun, run_id)
    if run is None:
        return GeoRunStatusResponse(runId=run_id, status="not_found", startedAt=None, finishedAt=None)

    assert_workspace_owner(db, run.workspace_id, user_id)

    return GeoRunStatusResponse(
        runId=run.id,
        status=run.status,
        startedAt=run.started_at.isoformat() if run.started_at else None,
        finishedAt=run.finished_at.isoformat() if run.finished_at else None,
    )
