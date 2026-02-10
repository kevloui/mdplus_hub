import time
from datetime import datetime
from typing import Any

import numpy as np

from src.glimps.adapter import GlimpsAdapter
from src.glimps.model_serializer import ModelSerializer
from src.infrastructure.database.models.job import JobStatus
from src.infrastructure.database.session import async_session_maker
from src.infrastructure.storage.file_storage import get_file_storage


async def train_glimps_model(
    ctx: dict[str, Any],
    job_id: str,
    cg_file_path: str,
    atomistic_file_path: str,
    model_id: str,
    glimps_options: dict[str, bool] | None = None,
) -> dict[str, Any]:
    from sqlalchemy import select, update

    from src.infrastructure.database.models.glimps_model import GlimpsModel
    from src.infrastructure.database.models.job import Job

    storage = get_file_storage()

    async with async_session_maker() as session:
        stmt = update(Job).where(Job.id == job_id).values(
            status=JobStatus.RUNNING,
            started_at=datetime.utcnow(),
            progress_percent=0.0,
            progress_message="Loading training data...",
        )
        await session.execute(stmt)
        await session.commit()

    try:
        cg_data = await storage.load_numpy(cg_file_path)
        atomistic_data = await storage.load_numpy(atomistic_file_path)

        async with async_session_maker() as session:
            stmt = update(Job).where(Job.id == job_id).values(
                progress_percent=10.0,
                progress_message="Training GLIMPS model...",
            )
            await session.execute(stmt)
            await session.commit()

        start_time = time.time()

        options = glimps_options or {}
        adapter = GlimpsAdapter.create_with_options(
            pca=options.get("pca", False),
            refine=options.get("refine", True),
            shave=options.get("shave", True),
            triangulate=options.get("triangulate", False),
        )

        def progress_callback(percent: float, message: str) -> None:
            pass

        adapter.fit(cg_data, atomistic_data, progress_callback)

        training_duration = time.time() - start_time

        async with async_session_maker() as session:
            stmt = update(Job).where(Job.id == job_id).values(
                progress_percent=80.0,
                progress_message="Saving trained model...",
            )
            await session.execute(stmt)
            await session.commit()

        model_bytes = ModelSerializer.serialize(adapter)
        model_path = f"models/{model_id}/model.pkl"
        await storage.save_bytes(model_path, model_bytes)

        async with async_session_maker() as session:
            stmt = update(GlimpsModel).where(GlimpsModel.id == model_id).values(
                is_trained=True,
                model_path=model_path,
                trained_at=datetime.utcnow(),
                training_duration_seconds=training_duration,
                training_metrics={
                    "cg_shape": list(cg_data.shape),
                    "atomistic_shape": list(atomistic_data.shape),
                },
            )
            await session.execute(stmt)

            stmt = update(Job).where(Job.id == job_id).values(
                status=JobStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                progress_percent=100.0,
                progress_message="Training complete",
            )
            await session.execute(stmt)
            await session.commit()

        return {"status": "success", "model_path": model_path}

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
