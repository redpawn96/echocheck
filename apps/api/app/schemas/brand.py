from datetime import datetime

from pydantic import BaseModel, Field


class BrandCreateRequest(BaseModel):
    workspace_id: str = Field(alias="workspaceId")
    name: str = Field(min_length=2, max_length=120)
    industry: str = Field(min_length=2, max_length=120)


class BrandResponse(BaseModel):
    id: str
    workspace_id: str = Field(alias="workspaceId")
    name: str
    industry: str
    created_at: datetime = Field(alias="createdAt")
