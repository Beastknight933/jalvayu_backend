import os
from uuid import UUID
from loguru import logger

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.ml import ModelRegistry, ModelStatus
from app.core.config import settings
from app.ml.pipelines.core import get_model_instance
from app.ml.models.base import ClimateModel

class ModelRegistryManager:
    """
    Manages the lifecycle of ML models, interacting with both the DB (metadata)
    and the filesystem/S3 (physical model weights).
    """

    def __init__(self):
        self.base_path = os.path.join(settings.DATA_STORAGE_BASE_PATH, settings.DATA_MODELS_DIR)
        os.makedirs(self.base_path, exist_ok=True)

    def _get_model_file_path(self, model_id: UUID, algorithm: str) -> str:
        """Generates a standard file path for a model."""
        extension = ".pkl" # Default, can be overridden based on algorithm (.h5, .pt)
        if algorithm == "xgboost":
            extension = ".json"
            
        return os.path.join(self.base_path, f"{model_id}{extension}")

    async def register_model(self, db: AsyncSession, model_id: UUID) -> str:
        """
        Called after training to assign a file path and update the DB registry.
        """
        query = select(ModelRegistry).where(ModelRegistry.id == model_id)
        result = await db.execute(query)
        model_record = result.scalars().first()
        
        if not model_record:
            raise ValueError(f"Model {model_id} not found in registry.")

        file_path = self._get_model_file_path(model_id, model_record.algorithm)
        
        # Update record
        model_record.model_path = file_path
        model_record.status = ModelStatus.READY
        await db.commit()
        
        return file_path

    async def load_model(self, db: AsyncSession, model_id: UUID) -> ClimateModel:
        """
        Loads a serialized model into memory based on its registry ID.
        """
        query = select(ModelRegistry).where(ModelRegistry.id == model_id)
        result = await db.execute(query)
        model_record = result.scalars().first()
        
        if not model_record:
            raise ValueError(f"Model {model_id} not found in registry.")
            
        if not model_record.model_path:
            raise ValueError(f"Model {model_id} has no physical path associated.")
            
        # Instantiate the correct wrapper
        model = get_model_instance(model_record.algorithm, model_record.configuration)
        
        # Load weights
        model.load(model_record.model_path)
        return model
        
    async def get_active_model(self, db: AsyncSession, target_variable: str) -> ClimateModel:
        """
        Fetches the currently active deployed model for a specific target (e.g. 'rainfall').
        """
        query = select(ModelRegistry).where(
            ModelRegistry.target_variable == target_variable,
            ModelRegistry.is_active_deployment == True,
            ModelRegistry.status == ModelStatus.READY
        )
        result = await db.execute(query)
        model_record = result.scalars().first()
        
        if not model_record:
            raise ValueError(f"No active model found for target {target_variable}")
            
        return await self.load_model(db, model_record.id)

registry_manager = ModelRegistryManager()
