from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from src.infrastructure.database.models.collaboration import ProjectCollaborator
from src.infrastructure.database.models.project import Project
from src.infrastructure.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    @property
    def _model(self) -> type[Project]:
        return Project

    async def get_user_projects(
        self, user_id: str, limit: int = 100, offset: int = 0
    ) -> list[Project]:
        stmt = (
            select(Project)
            .outerjoin(ProjectCollaborator)
            .where(
                or_(
                    Project.owner_id == user_id,
                    ProjectCollaborator.user_id == user_id,
                )
            )
            .distinct()
            .options(selectinload(Project.owner))
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_with_details(self, project_id: str) -> Project | None:
        stmt = (
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.owner),
                selectinload(Project.molecules),
                selectinload(Project.models),
                selectinload(Project.collaborators),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def user_has_access(self, project_id: str, user_id: str) -> bool:
        stmt = (
            select(Project.id)
            .outerjoin(ProjectCollaborator)
            .where(
                Project.id == project_id,
                or_(
                    Project.owner_id == user_id,
                    ProjectCollaborator.user_id == user_id,
                ),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
