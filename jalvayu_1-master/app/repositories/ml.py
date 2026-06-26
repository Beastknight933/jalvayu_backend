from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.ml import ModelRegistry, TrainingRun
from app.repositories.base import BaseRepository
from app.schemas.ml import ModelRegistryCreate, ModelRegistryUpdate, TrainingRunCreate, TrainingRunUpdate


class ModelRegistryRepository(BaseRepository[ModelRegistry, ModelRegistryCreate, ModelRegistryUpdate]):
    async def get_by_target(self, db: AsyncSession, *, target_variable: str) -> list[ModelRegistry]:
        query = select(ModelRegistry).where(ModelRegistry.target_variable == target_variable)
        result = await db.execute(query)
        return list(result.scalars().all())


class TrainingRunRepository(BaseRepository[TrainingRun, TrainingRunCreate, TrainingRunUpdate]):
    pass

registry_repo = ModelRegistryRepository(ModelRegistry)
training_repo = TrainingRunRepository(TrainingRun)
