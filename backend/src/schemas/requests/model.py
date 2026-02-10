from pydantic import BaseModel, Field


class CreateModelRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    project_id: str


class TrainModelRequest(BaseModel):
    cg_molecule_id: str
    atomistic_molecule_id: str
