"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, default=False),
        sa.Column("oauth_provider", sa.String(length=50), nullable=True),
        sa.Column("oauth_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_owner_id"), "projects", ["owner_id"])

    molecule_type = postgresql.ENUM(
        "coarse_grained", "atomistic", "backmapped",
        name="moleculetype",
        create_type=True,
    )
    file_format = postgresql.ENUM(
        "pdb", "gro", "xtc", "dcd", "mol2", "xyz",
        name="fileformat",
        create_type=True,
    )

    op.create_table(
        "molecules",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("molecule_type", molecule_type, nullable=False),
        sa.Column("file_format", file_format, nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("coordinates_path", sa.String(length=500), nullable=True),
        sa.Column("n_atoms", sa.Integer(), nullable=False),
        sa.Column("n_frames", sa.Integer(), nullable=False, default=1),
        sa.Column("topology_path", sa.String(length=500), nullable=True),
        sa.Column("source_molecule_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["source_molecule_id"], ["molecules.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_molecules_project_id"), "molecules", ["project_id"])

    op.create_table(
        "glimps_models",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("is_trained", sa.Boolean(), nullable=False, default=False),
        sa.Column("model_path", sa.String(length=500), nullable=True),
        sa.Column("training_config", postgresql.JSONB(), nullable=True),
        sa.Column("training_metrics", postgresql.JSONB(), nullable=True),
        sa.Column("cg_molecule_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("atomistic_molecule_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("trained_at", sa.DateTime(), nullable=True),
        sa.Column("training_duration_seconds", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["cg_molecule_id"], ["molecules.id"]),
        sa.ForeignKeyConstraint(["atomistic_molecule_id"], ["molecules.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_glimps_models_project_id"), "glimps_models", ["project_id"])

    job_type = postgresql.ENUM(
        "training", "inference", "file_processing",
        name="jobtype",
        create_type=True,
    )
    job_status = postgresql.ENUM(
        "pending", "queued", "running", "completed", "failed", "cancelled",
        name="jobstatus",
        create_type=True,
    )

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("job_type", job_type, nullable=False),
        sa.Column("status", job_status, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("input_params", postgresql.JSONB(), nullable=True),
        sa.Column("output_params", postgresql.JSONB(), nullable=True),
        sa.Column("progress_percent", sa.Float(), nullable=False, default=0.0),
        sa.Column("progress_message", sa.String(length=500), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["model_id"], ["glimps_models.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_jobs_user_id"), "jobs", ["user_id"])
    op.create_index(op.f("ix_jobs_project_id"), "jobs", ["project_id"])

    collaborator_role = postgresql.ENUM(
        "viewer", "editor", "admin",
        name="collaboratorrole",
        create_type=True,
    )

    op.create_table(
        "project_collaborators",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("role", collaborator_role, nullable=False),
        sa.Column("invited_by_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["invited_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_user"),
    )
    op.create_index(
        op.f("ix_project_collaborators_project_id"),
        "project_collaborators",
        ["project_id"],
    )
    op.create_index(
        op.f("ix_project_collaborators_user_id"),
        "project_collaborators",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_project_collaborators_user_id"), table_name="project_collaborators")
    op.drop_index(op.f("ix_project_collaborators_project_id"), table_name="project_collaborators")
    op.drop_table("project_collaborators")

    op.drop_index(op.f("ix_jobs_project_id"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_user_id"), table_name="jobs")
    op.drop_table("jobs")

    op.drop_index(op.f("ix_glimps_models_project_id"), table_name="glimps_models")
    op.drop_table("glimps_models")

    op.drop_index(op.f("ix_molecules_project_id"), table_name="molecules")
    op.drop_table("molecules")

    op.drop_index(op.f("ix_projects_owner_id"), table_name="projects")
    op.drop_table("projects")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS collaboratorrole")
    op.execute("DROP TYPE IF EXISTS jobstatus")
    op.execute("DROP TYPE IF EXISTS jobtype")
    op.execute("DROP TYPE IF EXISTS fileformat")
    op.execute("DROP TYPE IF EXISTS moleculetype")
