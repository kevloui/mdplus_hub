import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.session import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.project import Project


class MoleculeType(enum.Enum):
    COARSE_GRAINED = "coarse_grained"
    ATOMISTIC = "atomistic"
    BACKMAPPED = "backmapped"


class FileFormat(enum.Enum):
    PDB = "pdb"
    GRO = "gro"
    XTC = "xtc"
    DCD = "dcd"
    MOL2 = "mol2"
    XYZ = "xyz"


class Molecule(Base):
    __tablename__ = "molecules"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.id"),
        index=True,
    )
    molecule_type: Mapped[MoleculeType] = mapped_column(
        Enum(MoleculeType, values_callable=lambda x: [e.value for e in x]),
        default=MoleculeType.ATOMISTIC,
    )
    file_format: Mapped[FileFormat] = mapped_column(
        Enum(FileFormat, values_callable=lambda x: [e.value for e in x])
    )
    file_path: Mapped[str] = mapped_column(String(500))
    coordinates_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    n_atoms: Mapped[int] = mapped_column(Integer)
    n_frames: Mapped[int] = mapped_column(Integer, default=1)
    topology_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_molecule_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("molecules.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="molecules")
    source_molecule: Mapped["Molecule | None"] = relationship(remote_side=[id])
