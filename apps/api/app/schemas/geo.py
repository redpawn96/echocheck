from pydantic import BaseModel, Field


class GeoRunRequest(BaseModel):
    workspace_id: str = Field(alias="workspaceId")
    brand_id: str = Field(alias="brandId")
    industry: str
    providers: list[str]
    intents: list[str]


class GeoRunResponse(BaseModel):
    run_id: str = Field(alias="runId")
    status: str


class GeoRunStatusResponse(BaseModel):
    run_id: str = Field(alias="runId")
    status: str
    started_at: str | None = Field(default=None, alias="startedAt")
    finished_at: str | None = Field(default=None, alias="finishedAt")
