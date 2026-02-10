from pydantic import BaseModel, Field

from src.infrastructure.database.models.molecule import MoleculeType


class CreateMoleculeRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    project_id: str
    molecule_type: MoleculeType = MoleculeType.ATOMISTIC
