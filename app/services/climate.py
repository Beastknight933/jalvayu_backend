from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.climate import DatasetSource
from app.repositories.climate import climate_repo, version_repo
from app.schemas.climate import ClimateDatasetCreate, ClimateDatasetResponse, DatasetVersionCreate, DatasetVersionResponse
from app.core.redis import redis_client


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

    async def get_datasets(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> tuple[list[ClimateDatasetResponse], int]:
        datasets = await climate_repo.get_multi(db, skip=skip, limit=limit)
        total = await climate_repo.count(db)
        return [ClimateDatasetResponse.model_validate(d) for d in datasets], total
        
    async def get_dataset(self, db: AsyncSession, *, id: UUID) -> ClimateDatasetResponse:
        cache_key = f"climate_dataset:{id}"
        cached_data = await redis_client.get(cache_key)
        
        if cached_data:
            return ClimateDatasetResponse.model_validate_json(cached_data)
            
        dataset = await climate_repo.get(db, id=id)
        if not dataset:
            raise NotFoundException("Dataset not found")
            
        response = ClimateDatasetResponse.model_validate(dataset)
        await redis_client.setex(cache_key, 3600, response.model_dump_json())
        return response

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
