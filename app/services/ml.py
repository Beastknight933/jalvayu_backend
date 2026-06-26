from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.exceptions import NotFoundException
from app.repositories.ml import registry_repo, training_repo
from app.schemas.ml import ModelRegistryCreate, ModelRegistryResponse, TrainingRunCreate, TrainingRunResponse
from app.workers.tasks.ml_tasks import train_model_task

class MLService:
    """
    Business logic for managing ML models.
    """

    async def register_model(self, db: AsyncSession, obj_in: ModelRegistryCreate) -> ModelRegistryResponse:
        model = await registry_repo.create(db, obj_in=obj_in)
        return ModelRegistryResponse.model_validate(model)

    async def list_models(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ModelRegistryResponse]:
        models = await registry_repo.get_multi(db, skip=skip, limit=limit)
        return [ModelRegistryResponse.model_validate(m) for m in models]

    async def trigger_training(self, db: AsyncSession, model_id: UUID) -> TrainingRunResponse:
        """
        Creates a training run record and dispatches a Celery task.
        """
        model = await registry_repo.get(db, id=model_id)
        if not model:
            raise NotFoundException("Model not found")

        # 1. Create DB record
        run_in = TrainingRunCreate(model_id=model_id)
        run = await training_repo.create(db, obj_in=run_in)
        
        # 2. Dispatch Celery Task
        train_model_task.delay(str(run.id), str(model_id))
        
        return TrainingRunResponse.model_validate(run)

ml_service = MLService()
