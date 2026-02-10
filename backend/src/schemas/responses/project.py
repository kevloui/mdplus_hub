from datetime import datetime

from pydantic import BaseModel

from src.schemas.responses.auth import UserResponse


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    owner: UserResponse
    molecule_count: int = 0
    model_count: int = 0


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int
