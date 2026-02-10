from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.session import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.collaboration import ProjectCollaborator
    from src.infrastructure.database.models.glimps_model import GlimpsModel
    from src.infrastructure.database.models.molecule import Molecule
    from src.infrastructure.database.models.user import User


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    owner: Mapped["User"] = relationship(
        back_populates="projects",
        foreign_keys=[owner_id],
    )
    molecules: Mapped[list["Molecule"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    models: Mapped[list["GlimpsModel"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    collaborators: Mapped[list["ProjectCollaborator"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
