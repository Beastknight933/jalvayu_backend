from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.climate import DatasetSource
from app.repositories.climate import climate_repo, version_repo
from app.schemas.climate import ClimateDatasetCreate, ClimateDatasetResponse, DatasetVersionCreate, DatasetVersionResponse


class ClimateService:
    """
    Business logic for Climate Datasets.
    """

    async def create_dataset(self, db: AsyncSession, *, obj_in: ClimateDatasetCreate) -> ClimateDatasetResponse:
        existing = await climate_repo.get_by_name(db, name=obj_in.name)
        if existing:
            raise ConflictException(f"Dataset with name '{obj_in.name}' already exists.")
            
        dataset = await climate_repo.create(db, obj_in=obj_in)
        return ClimateDatasetResponse.model_validate(dataset)

    async def get_datasets(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[ClimateDatasetResponse]:
        datasets = await climate_repo.get_multi(db, skip=skip, limit=limit)
        return [ClimateDatasetResponse.model_validate(d) for d in datasets]
        
    async def get_dataset(self, db: AsyncSession, *, id: UUID) -> ClimateDatasetResponse:
        dataset = await climate_repo.get(db, id=id)
        if not dataset:
            raise NotFoundException("Dataset not found")
        return ClimateDatasetResponse.model_validate(dataset)

    async def add_version(self, db: AsyncSession, *, obj_in: DatasetVersionCreate) -> DatasetVersionResponse:
        dataset = await climate_repo.get(db, id=obj_in.dataset_id)
        if not dataset:
            raise NotFoundException("Dataset not found")
            
        existing = await version_repo.get_by_dataset_and_tag(db, dataset_id=str(obj_in.dataset_id), version_tag=obj_in.version_tag)
        if existing:
            raise ConflictException(f"Version '{obj_in.version_tag}' already exists for this dataset.")
            
        version = await version_repo.create(db, obj_in=obj_in)
        return DatasetVersionResponse.model_validate(version)


climate_service = ClimateService()
