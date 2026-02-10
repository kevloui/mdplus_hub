import os
from uuid import uuid4

import mdtraj as md
import numpy as np
from fastapi import APIRouter, Form, HTTPException, Query, UploadFile, status

from src.dependencies import CurrentUser, DbSession
from src.infrastructure.database.models.molecule import FileFormat, Molecule, MoleculeType
from src.infrastructure.repositories.project_repository import ProjectRepository
from src.infrastructure.storage.file_storage import get_file_storage
from src.schemas.responses.molecule import (
    MoleculeListResponse,
    MoleculeResponse,
    MoleculeStructureResponse,
)

router = APIRouter()

SUPPORTED_EXTENSIONS = {
    ".pdb": FileFormat.PDB,
    ".gro": FileFormat.GRO,
    ".xtc": FileFormat.XTC,
    ".dcd": FileFormat.DCD,
    ".mol2": FileFormat.MOL2,
    ".xyz": FileFormat.XYZ,
}

TOPOLOGY_FORMATS = {FileFormat.PDB, FileFormat.GRO, FileFormat.MOL2}
TRAJECTORY_FORMATS = {FileFormat.XTC, FileFormat.DCD}


def get_file_format(filename: str) -> FileFormat:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: {ext}. Supported: {list(SUPPORTED_EXTENSIONS.keys())}",
        )
    return SUPPORTED_EXTENSIONS[ext]


def parse_molecule_type(molecule_type: str) -> MoleculeType:
    type_map = {
        "coarse_grained": MoleculeType.COARSE_GRAINED,
        "atomistic": MoleculeType.ATOMISTIC,
        "backmapped": MoleculeType.BACKMAPPED,
    }
    if molecule_type not in type_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid molecule type: {molecule_type}. Valid: {list(type_map.keys())}",
        )
    return type_map[molecule_type]


@router.get("/", response_model=MoleculeListResponse)
async def list_molecules(
    db: DbSession,
    current_user: CurrentUser,
    project_id: str = Query(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> MoleculeListResponse:
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

    molecules = project.molecules[offset : offset + limit]
    return MoleculeListResponse(
        molecules=[MoleculeResponse.model_validate(m) for m in molecules],
        total=len(project.molecules),
    )


@router.post("/", response_model=MoleculeResponse, status_code=status.HTTP_201_CREATED)
async def upload_molecule(
    file: UploadFile,
    db: DbSession,
    current_user: CurrentUser,
    project_id: str = Form(...),
    name: str | None = Form(None),
    description: str | None = Form(None),
    molecule_type: str = Form("atomistic"),
) -> MoleculeResponse:
    project_repo = ProjectRepository(db)

    if not await project_repo.user_has_access(project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )

    file_format = get_file_format(file.filename)
    mol_type = parse_molecule_type(molecule_type)
    storage = get_file_storage()

    molecule_id = str(uuid4())
    file_content = await file.read()

    file_path = f"molecules/{project_id}/{molecule_id}/{file.filename}"
    await storage.save_bytes(file_path, file_content)

    n_atoms = 0
    n_frames = 1
    coordinates_path = None

    if file_format in TOPOLOGY_FORMATS:
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(
                suffix=os.path.splitext(file.filename)[1], delete=False
            ) as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name

            try:
                traj = md.load(tmp_path)
                n_atoms = traj.n_atoms
                n_frames = traj.n_frames

                coords = traj.xyz
                coords_path = f"molecules/{project_id}/{molecule_id}/coordinates.npy"
                await storage.save_numpy(coords_path, coords)
                coordinates_path = coords_path
            finally:
                os.unlink(tmp_path)
        except Exception:
            pass

    molecule = Molecule(
        id=molecule_id,
        name=name or os.path.splitext(file.filename)[0],
        description=description,
        project_id=project_id,
        molecule_type=mol_type,
        file_format=file_format,
        file_path=file_path,
        coordinates_path=coordinates_path,
        n_atoms=n_atoms,
        n_frames=n_frames,
    )

    db.add(molecule)
    await db.flush()
    await db.refresh(molecule)

    return MoleculeResponse.model_validate(molecule)


@router.get("/{molecule_id}", response_model=MoleculeResponse)
async def get_molecule(
    molecule_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> MoleculeResponse:
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    stmt = select(Molecule).where(Molecule.id == molecule_id).options(
        selectinload(Molecule.project)
    )
    result = await db.execute(stmt)
    molecule = result.scalar_one_or_none()

    if not molecule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Molecule not found",
        )

    project_repo = ProjectRepository(db)
    if not await project_repo.user_has_access(molecule.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Molecule not found",
        )

    return MoleculeResponse.model_validate(molecule)


@router.get("/{molecule_id}/structure", response_model=MoleculeStructureResponse)
async def get_molecule_structure(
    molecule_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> MoleculeStructureResponse:
    from sqlalchemy import select

    stmt = select(Molecule).where(Molecule.id == molecule_id)
    result = await db.execute(stmt)
    molecule = result.scalar_one_or_none()

    if not molecule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Molecule not found",
        )

    project_repo = ProjectRepository(db)
    if not await project_repo.user_has_access(molecule.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Molecule not found",
        )

    storage = get_file_storage()

    try:
        content = await storage.load_bytes(molecule.file_path)
        return MoleculeStructureResponse(
            id=molecule.id,
            name=molecule.name,
            format=molecule.file_format.value,
            content=content.decode("utf-8"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load structure: {str(e)}",
        )


@router.get("/{molecule_id}/coordinates")
async def get_molecule_coordinates(
    molecule_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> dict:
    from sqlalchemy import select

    stmt = select(Molecule).where(Molecule.id == molecule_id)
    result = await db.execute(stmt)
    molecule = result.scalar_one_or_none()

    if not molecule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Molecule not found",
        )

    project_repo = ProjectRepository(db)
    if not await project_repo.user_has_access(molecule.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Molecule not found",
        )

    if not molecule.coordinates_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No coordinates available for this molecule",
        )

    storage = get_file_storage()
    coords = await storage.load_numpy(molecule.coordinates_path)

    return {
        "id": molecule.id,
        "n_frames": int(coords.shape[0]),
        "n_atoms": int(coords.shape[1]),
        "coordinates": coords.tolist(),
    }


@router.delete("/{molecule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_molecule(
    molecule_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    from sqlalchemy import select

    stmt = select(Molecule).where(Molecule.id == molecule_id)
    result = await db.execute(stmt)
    molecule = result.scalar_one_or_none()

    if not molecule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Molecule not found",
        )

    project_repo = ProjectRepository(db)
    if not await project_repo.user_has_access(molecule.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Molecule not found",
        )

    storage = get_file_storage()

    try:
        await storage.delete(molecule.file_path)
        if molecule.coordinates_path:
            await storage.delete(molecule.coordinates_path)
    except Exception:
        pass

    await db.delete(molecule)
    await db.flush()
