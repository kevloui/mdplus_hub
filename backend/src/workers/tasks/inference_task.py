import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import mdtraj as md
import numpy as np

from src.glimps.model_serializer import ModelSerializer
from src.infrastructure.database.models.job import JobStatus
from src.infrastructure.database.models.molecule import FileFormat, Molecule, MoleculeType
from src.infrastructure.database.session import async_session_maker
from src.infrastructure.storage.file_storage import get_file_storage


async def run_inference(
    ctx: dict[str, Any],
    job_id: str,
    model_path: str,
    input_file_path: str,
    output_file_path: str,
    input_molecule_id: str,
    project_id: str,
    atomistic_file_path: str | None = None,
) -> dict[str, Any]:
    from sqlalchemy import select, update

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

        n_frames = int(atomistic_coords.shape[0])
        n_atoms = int(atomistic_coords.shape[1])

        async with async_session_maker() as session:
            stmt = update(Job).where(Job.id == job_id).values(
                progress_percent=90.0,
                progress_message="Creating backmapped molecule...",
            )
            await session.execute(stmt)
            await session.commit()

        molecule_id = str(uuid4())

        async with async_session_maker() as session:
            input_stmt = select(Molecule).where(Molecule.id == input_molecule_id)
            input_result = await session.execute(input_stmt)
            input_molecule = input_result.scalar_one_or_none()
            input_name = input_molecule.name if input_molecule else "CG structure"

        pdb_content = await _create_pdb_from_template(
            storage, atomistic_file_path, atomistic_coords, n_atoms
        )

        file_path = f"molecules/{project_id}/{molecule_id}/structure.pdb"
        await storage.save_bytes(file_path, pdb_content.encode("utf-8"))

        coords_path = f"molecules/{project_id}/{molecule_id}/coordinates.npy"
        await storage.save_numpy(coords_path, atomistic_coords)

        async with async_session_maker() as session:
            molecule = Molecule(
                id=molecule_id,
                name=f"Backmapped {input_name}",
                description=f"Backmapped structure from inference job {job_id[:8]}",
                project_id=project_id,
                molecule_type=MoleculeType.BACKMAPPED,
                file_format=FileFormat.PDB,
                file_path=file_path,
                coordinates_path=coords_path,
                n_atoms=n_atoms,
                n_frames=n_frames,
                source_molecule_id=input_molecule_id,
            )
            session.add(molecule)
            await session.commit()

        async with async_session_maker() as session:
            stmt = update(Job).where(Job.id == job_id).values(
                status=JobStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                progress_percent=100.0,
                progress_message="Inference complete",
                output_params={
                    "output_path": output_file_path,
                    "n_frames": n_frames,
                    "n_atoms": n_atoms,
                    "molecule_id": molecule_id,
                },
            )
            await session.execute(stmt)
            await session.commit()

        return {
            "status": "success",
            "output_path": output_file_path,
            "n_frames": n_frames,
            "n_atoms": n_atoms,
            "molecule_id": molecule_id,
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


async def _create_pdb_from_template(
    storage, atomistic_file_path: str | None, coords: np.ndarray, n_atoms: int
) -> str:
    if atomistic_file_path:
        try:
            pdb_bytes = await storage.load_bytes(atomistic_file_path)

            with tempfile.NamedTemporaryFile(suffix=".pdb", delete=False) as f:
                f.write(pdb_bytes)
                temp_path = Path(f.name)

            try:
                template_traj = md.load(str(temp_path))
                new_traj = md.Trajectory(
                    xyz=coords.astype(np.float32),
                    topology=template_traj.topology,
                )

                output_path = temp_path.with_suffix(".output.pdb")
                new_traj.save_pdb(str(output_path))

                pdb_content = output_path.read_text()
                output_path.unlink(missing_ok=True)
                return pdb_content
            finally:
                temp_path.unlink(missing_ok=True)

        except Exception:
            pass

    return _coordinates_to_pdb(coords, n_atoms)


def _coordinates_to_pdb(coords: np.ndarray, n_atoms: int) -> str:
    lines = []
    for i in range(n_atoms):
        x, y, z = coords[0][i] * 10
        lines.append(
            f"ATOM  {i+1:5d}  CA  ALA A{i+1:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C"
        )
    lines.append("END")
    return "\n".join(lines)
