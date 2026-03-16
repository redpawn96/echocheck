from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.models import User, Workspace
from app.db.session import get_db
from app.schemas.workspace import WorkspaceCreateRequest, WorkspaceResponse

router = APIRouter(prefix="/v1/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceResponse)
def create_workspace(
    payload: WorkspaceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    workspace = Workspace(owner_user_id=current_user.id, name=payload.name.strip())
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return WorkspaceResponse(id=workspace.id, name=workspace.name, createdAt=workspace.created_at)


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[WorkspaceResponse]:
    workspaces = db.scalars(
        select(Workspace).where(Workspace.owner_user_id == current_user.id).order_by(Workspace.created_at.desc())
    ).all()

    return [
        WorkspaceResponse(id=workspace.id, name=workspace.name, createdAt=workspace.created_at)
        for workspace in workspaces
    ]


def assert_workspace_owner(db: Session, workspace_id: str, user_id: str) -> Workspace:
    workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    if workspace.owner_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed for workspace")

    return workspace
