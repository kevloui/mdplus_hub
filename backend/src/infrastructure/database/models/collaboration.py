import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.session import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.project import Project
    from src.infrastructure.database.models.user import User


class CollaboratorRole(enum.Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"


class ProjectCollaborator(Base):
    __tablename__ = "project_collaborators"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_user"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.id"),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        index=True,
    )
    role: Mapped[CollaboratorRole] = mapped_column(
        Enum(CollaboratorRole, values_callable=lambda x: [e.value for e in x]),
        default=CollaboratorRole.VIEWER,
    )
    invited_by_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
    )
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="collaborators")
    user: Mapped["User"] = relationship(
        back_populates="collaborations",
        foreign_keys=[user_id],
    )
    invited_by: Mapped["User"] = relationship(foreign_keys=[invited_by_id])
