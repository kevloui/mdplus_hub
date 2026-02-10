from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from src.dependencies import CurrentUser, DbSession
from src.infrastructure.database.models.glimps_model import GlimpsModel
from src.infrastructure.database.models.project import Project
from src.infrastructure.repositories.project_repository import ProjectRepository
from src.schemas.requests.project import CreateProjectRequest, UpdateProjectRequest
from src.schemas.responses.auth import UserResponse
from src.schemas.responses.project import (
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
)

router = APIRouter()


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    db: DbSession,
    current_user: CurrentUser,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> ProjectListResponse:
    repository = ProjectRepository(db)
    projects = await repository.get_user_projects(current_user.id, limit, offset)
    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=len(projects),
    )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> ProjectResponse:
    repository = ProjectRepository(db)
    project = Project(
        name=request.name,
        description=request.description,
        owner_id=current_user.id,
    )
    project = await repository.create(project)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> ProjectDetailResponse:
    repository = ProjectRepository(db)

    if not await repository.user_has_access(project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    project = await repository.get_with_details(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return ProjectDetailResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        owner=UserResponse.model_validate(project.owner),
        molecule_count=len(project.molecules),
        model_count=len(project.models),
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> ProjectResponse:
    repository = ProjectRepository(db)

    project = await repository.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can update this project",
        )

    if request.name is not None:
        project.name = request.name
    if request.description is not None:
        project.description = request.description

    project = await repository.update(project)
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    repository = ProjectRepository(db)

    project = await repository.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can delete this project",
        )

    await repository.delete(project)


@router.get("/stats/trained-models")
async def get_trained_models_count(
    db: DbSession,
    current_user: CurrentUser,
) -> dict:
    stmt = (
        select(func.count(GlimpsModel.id))
        .join(Project, GlimpsModel.project_id == Project.id)
        .where(Project.owner_id == current_user.id)
        .where(GlimpsModel.is_trained == True)
    )
    result = await db.execute(stmt)
    count = result.scalar() or 0
    return {"trained_models_count": count}
