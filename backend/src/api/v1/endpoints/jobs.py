from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.dependencies import CurrentUser, DbSession
from src.infrastructure.database.models.job import Job, JobStatus
from src.infrastructure.repositories.project_repository import ProjectRepository
from src.schemas.responses.job import JobListResponse, JobResponse

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
