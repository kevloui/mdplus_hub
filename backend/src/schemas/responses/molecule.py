from datetime import datetime

from pydantic import BaseModel

from src.infrastructure.database.models.molecule import FileFormat, MoleculeType


class MoleculeResponse(BaseModel):
    id: str
    name: str
    description: str | None
    project_id: str
    molecule_type: MoleculeType
    file_format: FileFormat
    n_atoms: int
    n_frames: int
    source_molecule_id: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class MoleculeListResponse(BaseModel):
    molecules: list[MoleculeResponse]
    total: int


class MoleculeStructureResponse(BaseModel):
    id: str
    name: str
    format: str
    content: str
