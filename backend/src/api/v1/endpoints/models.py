from uuid import uuid4

from arq import create_pool
from fastapi import APIRouter, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select

from src.dependencies import CurrentUser, DbSession
from src.infrastructure.database.models.glimps_model import GlimpsModel
from src.infrastructure.database.models.job import Job, JobStatus, JobType
from src.infrastructure.database.models.molecule import Molecule
from src.infrastructure.repositories.project_repository import ProjectRepository
from src.infrastructure.storage.file_storage import get_file_storage
from src.schemas.requests.model import CreateModelRequest, GlimpsOptionsRequest
from src.schemas.responses.model import ModelListResponse, ModelResponse, TrainingJobResponse
from src.workers.settings import WorkerSettings

router = APIRouter()


@router.get("/", response_model=ModelListResponse)
async def list_models(
    db: DbSession,
    current_user: CurrentUser,
    project_id: str = Query(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> ModelListResponse:
    project_repo = ProjectRepository(db)

    if not await project_repo.user_has_access(project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    project = await project_repo.get_with_details(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    models = project.models[offset : offset + limit]
    return ModelListResponse(
        models=[ModelResponse.model_validate(m) for m in models],
        total=len(project.models),
    )


@router.post("/", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    request: CreateModelRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> ModelResponse:
    project_repo = ProjectRepository(db)

    if not await project_repo.user_has_access(request.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    model = GlimpsModel(
        name=request.name,
        description=request.description,
        project_id=request.project_id,
    )
    db.add(model)
    await db.flush()
    await db.refresh(model)

    return ModelResponse.model_validate(model)


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> ModelResponse:
    stmt = select(GlimpsModel).where(GlimpsModel.id == model_id)
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    project_repo = ProjectRepository(db)
    if not await project_repo.user_has_access(model.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    return ModelResponse.model_validate(model)


@router.post("/{model_id}/train", response_model=TrainingJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def train_model(
    model_id: str,
    db: DbSession,
    current_user: CurrentUser,
    cg_molecule_id: str = Form(...),
    atomistic_molecule_id: str = Form(...),
    pca: bool = Form(False),
    refine: bool = Form(True),
    shave: bool = Form(True),
    triangulate: bool = Form(False),
) -> TrainingJobResponse:
    stmt = select(GlimpsModel).where(GlimpsModel.id == model_id)
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    project_repo = ProjectRepository(db)
    if not await project_repo.user_has_access(model.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    if model.is_trained:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model is already trained",
        )

    cg_stmt = select(Molecule).where(Molecule.id == cg_molecule_id)
    cg_result = await db.execute(cg_stmt)
    cg_molecule = cg_result.scalar_one_or_none()

    if not cg_molecule or cg_molecule.project_id != model.project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CG molecule not found in this project",
        )

    if not cg_molecule.coordinates_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CG molecule has no coordinates",
        )

    atomistic_stmt = select(Molecule).where(Molecule.id == atomistic_molecule_id)
    atomistic_result = await db.execute(atomistic_stmt)
    atomistic_molecule = atomistic_result.scalar_one_or_none()

    if not atomistic_molecule or atomistic_molecule.project_id != model.project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Atomistic molecule not found in this project",
        )

    if not atomistic_molecule.coordinates_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Atomistic molecule has no coordinates",
        )

    glimps_options = {
        "pca": pca,
        "refine": refine,
        "shave": shave,
        "triangulate": triangulate,
    }

    model.cg_molecule_id = cg_molecule_id
    model.atomistic_molecule_id = atomistic_molecule_id
    model.training_config = glimps_options
    await db.flush()

    job = Job(
        job_type=JobType.TRAINING,
        status=JobStatus.PENDING,
        user_id=current_user.id,
        project_id=model.project_id,
        model_id=model_id,
        input_params={
            "cg_molecule_id": cg_molecule_id,
            "atomistic_molecule_id": atomistic_molecule_id,
            "glimps_options": glimps_options,
        },
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)

    redis_pool = await create_pool(WorkerSettings.redis_settings)
    await redis_pool.enqueue_job(
        "train_glimps_model",
        job.id,
        cg_molecule.coordinates_path,
        atomistic_molecule.coordinates_path,
        model_id,
        glimps_options,
    )
    await redis_pool.close()

    stmt = select(Job).where(Job.id == job.id)
    result = await db.execute(stmt)
    job = result.scalar_one()

    job.status = JobStatus.QUEUED
    await db.flush()

    return TrainingJobResponse(
        job_id=job.id,
        model_id=model_id,
        status=job.status.value,
    )


@router.post("/{model_id}/inference", status_code=status.HTTP_202_ACCEPTED)
async def run_inference(
    model_id: str,
    db: DbSession,
    current_user: CurrentUser,
    input_molecule_id: str = Form(...),
) -> dict:
    stmt = select(GlimpsModel).where(GlimpsModel.id == model_id)
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    project_repo = ProjectRepository(db)
    if not await project_repo.user_has_access(model.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    if not model.is_trained or not model.model_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model is not trained yet",
        )

    input_stmt = select(Molecule).where(Molecule.id == input_molecule_id)
    input_result = await db.execute(input_stmt)
    input_molecule = input_result.scalar_one_or_none()

    if not input_molecule or input_molecule.project_id != model.project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input molecule not found in this project",
        )

    if not input_molecule.coordinates_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input molecule has no coordinates",
        )

    output_file_path = f"inference/{model.project_id}/{model_id}/{str(uuid4())}/output.npy"

    job = Job(
        job_type=JobType.INFERENCE,
        status=JobStatus.PENDING,
        user_id=current_user.id,
        project_id=model.project_id,
        model_id=model_id,
        input_params={
            "input_molecule_id": input_molecule_id,
            "output_file_path": output_file_path,
        },
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)

    atomistic_molecule_stmt = select(Molecule).where(
        Molecule.id == model.atomistic_molecule_id
    )
    atomistic_result = await db.execute(atomistic_molecule_stmt)
    atomistic_molecule = atomistic_result.scalar_one_or_none()

    atomistic_file_path = atomistic_molecule.file_path if atomistic_molecule else None

    redis_pool = await create_pool(WorkerSettings.redis_settings)
    await redis_pool.enqueue_job(
        "run_inference",
        job.id,
        model.model_path,
        input_molecule.coordinates_path,
        output_file_path,
        input_molecule_id,
        model.project_id,
        atomistic_file_path,
    )
    await redis_pool.close()

    job.status = JobStatus.QUEUED
    await db.flush()

    return {
        "job_id": job.id,
        "model_id": model_id,
        "status": job.status.value,
    }


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    stmt = select(GlimpsModel).where(GlimpsModel.id == model_id)
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    project_repo = ProjectRepository(db)
    if not await project_repo.user_has_access(model.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    if model.model_path:
        storage = get_file_storage()
        try:
            await storage.delete(model.model_path)
        except Exception:
            pass

    await db.delete(model)
    await db.flush()
