from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.session import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.job import Job
    from src.infrastructure.database.models.molecule import Molecule
    from src.infrastructure.database.models.project import Project


class GlimpsModel(Base):
    __tablename__ = "glimps_models"

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
    is_trained: Mapped[bool] = mapped_column(Boolean, default=False)
    model_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    training_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    training_metrics: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    cg_molecule_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("molecules.id"),
        nullable=True,
    )
    atomistic_molecule_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("molecules.id"),
        nullable=True,
    )
    trained_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    training_duration_seconds: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    project: Mapped["Project"] = relationship(back_populates="models")
    cg_molecule: Mapped["Molecule | None"] = relationship(
        foreign_keys=[cg_molecule_id]
    )
    atomistic_molecule: Mapped["Molecule | None"] = relationship(
        foreign_keys=[atomistic_molecule_id]
    )
    jobs: Mapped[list["Job"]] = relationship(back_populates="model")
