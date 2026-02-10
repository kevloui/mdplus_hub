from datetime import datetime

from pydantic import BaseModel


class ModelResponse(BaseModel):
    id: str
    name: str
    description: str | None
    project_id: str
    is_trained: bool
    training_config: dict | None
    training_metrics: dict | None
    cg_molecule_id: str | None
    atomistic_molecule_id: str | None
    trained_at: datetime | None
    training_duration_seconds: float | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelListResponse(BaseModel):
    models: list[ModelResponse]
    total: int


class TrainingJobResponse(BaseModel):
    job_id: str
    model_id: str
    status: str
