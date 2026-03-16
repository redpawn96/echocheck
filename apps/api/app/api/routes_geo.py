from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.routes_workspaces import assert_workspace_owner
from app.db.models import User
from app.db.session import get_db
from app.schemas.geo import GeoRunRequest, GeoRunResponse, GeoRunStatusResponse
from app.services.geo_service import get_geo_run_status, queue_geo_run

router = APIRouter(prefix="/v1/geo", tags=["geo"])


@router.post("/runs", response_model=GeoRunResponse)
def create_geo_run(
    payload: GeoRunRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GeoRunResponse:
    assert_workspace_owner(db, payload.workspace_id, current_user.id)
    return queue_geo_run(db, payload)


@router.get("/runs/{run_id}", response_model=GeoRunStatusResponse)
def read_geo_run(
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GeoRunStatusResponse:
    return get_geo_run_status(db, run_id, current_user.id)
