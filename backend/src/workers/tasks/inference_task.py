from datetime import datetime
from typing import Any

from src.glimps.model_serializer import ModelSerializer
from src.infrastructure.database.models.job import JobStatus
from src.infrastructure.database.session import async_session_maker
from src.infrastructure.storage.file_storage import get_file_storage


async def run_inference(
    ctx: dict[str, Any],
    job_id: str,
    model_path: str,
    input_file_path: str,
    output_file_path: str,
) -> dict[str, Any]:
    from sqlalchemy import update

    from src.infrastructure.database.models.job import Job

    storage = get_file_storage()

    async with async_session_maker() as session:
        stmt = update(Job).where(Job.id == job_id).values(
            status=JobStatus.RUNNING,
            started_at=datetime.utcnow(),
            progress_percent=0.0,
            progress_message="Loading model...",
        )
        await session.execute(stmt)
        await session.commit()

    try:
        model_bytes = await storage.load_bytes(model_path)
        adapter = ModelSerializer.deserialize(model_bytes)

        async with async_session_maker() as session:
            stmt = update(Job).where(Job.id == job_id).values(
                progress_percent=20.0,
                progress_message="Loading input coordinates...",
            )
            await session.execute(stmt)
            await session.commit()

        cg_coords = await storage.load_numpy(input_file_path)

        async with async_session_maker() as session:
            stmt = update(Job).where(Job.id == job_id).values(
                progress_percent=40.0,
                progress_message="Running inference...",
            )
            await session.execute(stmt)
            await session.commit()

        atomistic_coords = adapter.transform(cg_coords)

        async with async_session_maker() as session:
            stmt = update(Job).where(Job.id == job_id).values(
                progress_percent=80.0,
                progress_message="Saving results...",
            )
            await session.execute(stmt)
            await session.commit()

        await storage.save_numpy(output_file_path, atomistic_coords)

        async with async_session_maker() as session:
            stmt = update(Job).where(Job.id == job_id).values(
                status=JobStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                progress_percent=100.0,
                progress_message="Inference complete",
                output_params={
                    "output_path": output_file_path,
                    "n_frames": int(atomistic_coords.shape[0]),
                    "n_atoms": int(atomistic_coords.shape[1]),
                },
            )
            await session.execute(stmt)
            await session.commit()

        return {
            "status": "success",
            "output_path": output_file_path,
            "n_frames": atomistic_coords.shape[0],
            "n_atoms": atomistic_coords.shape[1],
        }

    except Exception as e:
        async with async_session_maker() as session:
            stmt = update(Job).where(Job.id == job_id).values(
                status=JobStatus.FAILED,
                completed_at=datetime.utcnow(),
                error_message=str(e),
            )
            await session.execute(stmt)
            await session.commit()

        raise
