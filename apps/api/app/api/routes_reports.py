from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.models import Brand, User
from app.db.session import get_db
from app.schemas.report import WeeklyReportResponse
from app.services.report_service import get_or_compute_weekly_report

router = APIRouter(prefix="/v1/reports", tags=["reports"])


@router.get("/weekly", response_model=WeeklyReportResponse)
def get_weekly_report(
    brand_id: str = Query(alias="brandId"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WeeklyReportResponse:
    brand = db.get(Brand, brand_id)
    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

    if brand.workspace is None or brand.workspace.owner_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed for brand")

    return get_or_compute_weekly_report(db, brand_id)
