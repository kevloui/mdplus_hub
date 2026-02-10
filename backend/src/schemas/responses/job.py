from datetime import datetime

from pydantic import BaseModel

from src.infrastructure.database.models.job import JobStatus, JobType


class JobResponse(BaseModel):
    id: str
    job_type: JobType
    status: JobStatus
    project_id: str
    model_id: str | None
    input_params: dict | None
    output_params: dict | None
    progress_percent: float
    progress_message: str | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
