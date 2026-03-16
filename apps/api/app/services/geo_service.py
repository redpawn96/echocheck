import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.routes_workspaces import assert_workspace_owner
from app.core.celery_client import enqueue_geo_run
from app.db.models import Brand, GeoRun
from app.schemas.geo import GeoRunRequest, GeoRunResponse, GeoRunStatusResponse

logger = logging.getLogger(__name__)


def queue_geo_run(db: Session, payload: GeoRunRequest) -> GeoRunResponse:
    brand = db.get(Brand, payload.brand_id)
    if brand is None or brand.workspace_id != payload.workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found in workspace")

    run = GeoRun(
        workspace_id=payload.workspace_id,
        brand_id=payload.brand_id,
        status="queued",
        providers_csv=",".join(payload.providers),
        intents_csv="\n".join(payload.intents),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

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
