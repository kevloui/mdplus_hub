import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.session import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.glimps_model import GlimpsModel
    from src.infrastructure.database.models.project import Project
    from src.infrastructure.database.models.user import User


class JobType(enum.Enum):
    TRAINING = "training"
    INFERENCE = "inference"
    FILE_PROCESSING = "file_processing"


class JobStatus(enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    job_type: Mapped[JobType] = mapped_column(
        Enum(JobType, values_callable=lambda x: [e.value for e in x])
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, values_callable=lambda x: [e.value for e in x]),
        default=JobStatus.PENDING,
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.id"),
        index=True,
    )
    model_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("glimps_models.id"),
        nullable=True,
    )
    input_params: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_params: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0)
    progress_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="jobs")
    project: Mapped["Project"] = relationship()
    model: Mapped["GlimpsModel | None"] = relationship(back_populates="jobs")
