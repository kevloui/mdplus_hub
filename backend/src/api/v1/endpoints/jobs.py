from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.dependencies import CurrentUser, DbSession
from src.infrastructure.database.models.job import Job, JobStatus, JobType
from src.infrastructure.database.models.molecule import FileFormat, Molecule, MoleculeType
from src.infrastructure.repositories.project_repository import ProjectRepository
from src.infrastructure.storage.file_storage import get_file_storage
from src.schemas.responses.job import JobListResponse, JobResponse
from src.schemas.responses.molecule import MoleculeResponse

router = APIRouter()


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    db: DbSession,
    current_user: CurrentUser,
    project_id: str | None = Query(None),
    job_status: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> JobListResponse:
    stmt = select(Job).where(Job.user_id == current_user.id)

    if project_id:
        project_repo = ProjectRepository(db)
        if not await project_repo.user_has_access(project_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        stmt = stmt.where(Job.project_id == project_id)

    if job_status:
        try:
            status_enum = JobStatus(job_status)
            stmt = stmt.where(Job.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {job_status}. Valid: {[s.value for s in JobStatus]}",
            )

    stmt = stmt.order_by(Job.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    jobs = list(result.scalars().all())

    count_stmt = select(Job).where(Job.user_id == current_user.id)
    if project_id:
        count_stmt = count_stmt.where(Job.project_id == project_id)
    if job_status:
        count_stmt = count_stmt.where(Job.status == JobStatus(job_status))

    count_result = await db.execute(count_stmt)
    total = len(list(count_result.scalars().all()))

    return JobListResponse(
        jobs=[JobResponse.model_validate(j) for j in jobs],
        total=total,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> JobResponse:
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if job.user_id != current_user.id:
        project_repo = ProjectRepository(db)
        if not await project_repo.user_has_access(job.project_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

    return JobResponse.model_validate(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_job(
    job_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this job",
        )

    if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status: {job.status.value}",
        )

    job.status = JobStatus.CANCELLED
    await db.flush()


@router.get("/{job_id}/download")
async def download_job_result(
    job_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if job.user_id != current_user.id:
        project_repo = ProjectRepository(db)
        if not await project_repo.user_has_access(job.project_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not completed",
        )

    if job.job_type != JobType.INFERENCE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only inference jobs have downloadable results",
        )

    if not job.output_params or "output_path" not in job.output_params:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No output file available",
        )

    storage = get_file_storage()
    try:
        data = await storage.load_bytes(job.output_params["output_path"])
        return Response(
            content=data,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="inference_result_{job_id}.npy"'
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load result file: {str(e)}",
        )


@router.post("/{job_id}/create-molecule", response_model=MoleculeResponse)
async def create_molecule_from_job(
    job_id: str,
    db: DbSession,
    current_user: CurrentUser,
    name: str | None = None,
) -> MoleculeResponse:
    import io
    import tempfile
    from uuid import uuid4

    import mdtraj as md
    import numpy as np

    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if job.user_id != current_user.id:
        project_repo = ProjectRepository(db)
        if not await project_repo.user_has_access(job.project_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not completed",
        )

    if job.job_type != JobType.INFERENCE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only inference jobs can create molecules",
        )

    if not job.output_params or "output_path" not in job.output_params:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No output file available",
        )

    input_molecule_id = job.input_params.get("input_molecule_id") if job.input_params else None
    if not input_molecule_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot determine source molecule",
        )

    input_stmt = select(Molecule).where(Molecule.id == input_molecule_id)
    input_result = await db.execute(input_stmt)
    input_molecule = input_result.scalar_one_or_none()

    storage = get_file_storage()

    coords = await storage.load_numpy(job.output_params["output_path"])
    n_frames, n_atoms, _ = coords.shape

    molecule_id = str(uuid4())
    molecule_name = name or f"Backmapped from {input_molecule.name if input_molecule else 'inference'}"

    pdb_content = _coordinates_to_pdb(coords[0], n_atoms)

    file_path = f"molecules/{job.project_id}/{molecule_id}/structure.pdb"
    await storage.save_bytes(file_path, pdb_content.encode("utf-8"))

    coords_path = f"molecules/{job.project_id}/{molecule_id}/coordinates.npy"
    await storage.save_numpy(coords_path, coords)

    molecule = Molecule(
        id=molecule_id,
        name=molecule_name,
        description=f"Backmapped structure from inference job {job_id[:8]}",
        project_id=job.project_id,
        molecule_type=MoleculeType.BACKMAPPED,
        file_format=FileFormat.PDB,
        file_path=file_path,
        coordinates_path=coords_path,
        n_atoms=n_atoms,
        n_frames=n_frames,
        source_molecule_id=input_molecule_id,
    )

    db.add(molecule)
    await db.flush()
    await db.refresh(molecule)

    return MoleculeResponse.model_validate(molecule)


def _coordinates_to_pdb(coords, n_atoms: int) -> str:
    lines = []
    for i in range(n_atoms):
        x, y, z = coords[i] * 10
        lines.append(
            f"ATOM  {i+1:5d}  CA  ALA A{i+1:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C"
        )
    lines.append("END")
    return "\n".join(lines)
