from sqlalchemy import select

from src.infrastructure.database.models.user import User
from src.infrastructure.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    @property
    def _model(self) -> type[User]:
        return User

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_oauth(
        self, provider: str, oauth_id: str
    ) -> User | None:
        stmt = select(User).where(
            User.oauth_provider == provider,
            User.oauth_id == oauth_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
