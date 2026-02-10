from pydantic import BaseModel, Field


class CreateModelRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    project_id: str


class GlimpsOptionsRequest(BaseModel):
    pca: bool = Field(
        default=False,
        description="Use PCA transform step for dimensionality reduction"
    )
    refine: bool = Field(
        default=True,
        description="Use elastic network minimizer to improve geometry"
    )
    shave: bool = Field(
        default=True,
        description="Calculate terminal atom positions using Z-matrix"
    )
    triangulate: bool = Field(
        default=False,
        description="Replace core MLR step with triangulation method"
    )


class TrainModelRequest(BaseModel):
    cg_molecule_id: str
    atomistic_molecule_id: str
    glimps_options: GlimpsOptionsRequest = Field(default_factory=GlimpsOptionsRequest)
