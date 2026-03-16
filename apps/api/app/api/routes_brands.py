from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.routes_workspaces import assert_workspace_owner
from app.db.models import Brand, User
from app.db.session import get_db
from app.schemas.brand import BrandCreateRequest, BrandResponse

router = APIRouter(prefix="/v1/brands", tags=["brands"])


@router.post("", response_model=BrandResponse)
def create_brand(
    payload: BrandCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BrandResponse:
    assert_workspace_owner(db, payload.workspace_id, current_user.id)

    brand = Brand(
        workspace_id=payload.workspace_id,
        name=payload.name.strip(),
        industry=payload.industry.strip(),
    )
    db.add(brand)
    db.commit()
    db.refresh(brand)

    return BrandResponse(
        id=brand.id,
        workspaceId=brand.workspace_id,
        name=brand.name,
        industry=brand.industry,
        createdAt=brand.created_at,
    )


@router.get("", response_model=list[BrandResponse])
def list_brands(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[BrandResponse]:
    assert_workspace_owner(db, workspace_id, current_user.id)

    brands = db.scalars(select(Brand).where(Brand.workspace_id == workspace_id).order_by(Brand.created_at.desc())).all()
    return [
        BrandResponse(
            id=brand.id,
            workspaceId=brand.workspace_id,
            name=brand.name,
            industry=brand.industry,
            createdAt=brand.created_at,
        )
        for brand in brands
    ]
