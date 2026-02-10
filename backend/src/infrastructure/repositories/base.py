from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.session import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    def __init__(self, session: AsyncSession):
        self._session = session

    @property
    @abstractmethod
    def _model(self) -> type[ModelType]:
        pass

    async def get_by_id(self, entity_id: str) -> ModelType | None:
        return await self._session.get(self._model, entity_id)

    async def get_all(
        self, limit: int = 100, offset: int = 0
    ) -> list[ModelType]:
        stmt = select(self._model).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: ModelType) -> ModelType:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: ModelType) -> ModelType:
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity: ModelType) -> None:
        await self._session.delete(entity)
        await self._session.flush()
