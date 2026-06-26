from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.climate import ClimateDataset, DatasetVersion, DatasetSource
from app.repositories.base import BaseRepository
from app.schemas.climate import ClimateDatasetCreate, ClimateDatasetUpdate, DatasetVersionCreate


class ClimateDatasetRepository(BaseRepository[ClimateDataset, ClimateDatasetCreate, ClimateDatasetUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[ClimateDataset]:
        query = select(ClimateDataset).where(ClimateDataset.name == name)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_source(self, db: AsyncSession, *, source: DatasetSource) -> list[ClimateDataset]:
        query = select(ClimateDataset).where(ClimateDataset.source == source)
        result = await db.execute(query)
        return list(result.scalars().all())


class DatasetVersionRepository(BaseRepository[DatasetVersion, DatasetVersionCreate, DatasetVersionCreate]):
    async def get_by_dataset_and_tag(self, db: AsyncSession, *, dataset_id: str, version_tag: str) -> Optional[DatasetVersion]:
        query = select(DatasetVersion).where(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.version_tag == version_tag
        )
        result = await db.execute(query)
        return result.scalars().first()


climate_repo = ClimateDatasetRepository(ClimateDataset)
version_repo = DatasetVersionRepository(DatasetVersion)
