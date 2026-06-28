import asyncio
from uuid import UUID
from loguru import logger
from datetime import datetime, timezone

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.repositories.ml import registry_repo, training_repo
from app.schemas.ml import TrainingRunUpdate, ModelRegistryUpdate
from app.models.ml import ModelStatus
from app.ml.pipelines.core import MLPipeline
from app.ml.registry.manager import registry_manager


async def async_train_model(run_id: UUID, model_id: UUID):
    """
    Asynchronous implementation of the training task.
    """
    async with AsyncSessionLocal() as db:
        run = await training_repo.get(db, id=run_id)
        model_record = await registry_repo.get(db, id=model_id)
        
        if not run or not model_record:
            logger.error("Run or Model not found.")
            return
            
        try:
            # Update DB Status
            await registry_repo.update(db, db_obj=model_record, obj_in=ModelRegistryUpdate(status=ModelStatus.TRAINING))
            
            # Execute Pipeline
            pipeline = MLPipeline(algorithm=model_record.algorithm, config=model_record.configuration)
            
            # In a real scenario, dataset_version_id comes from model_record
            metrics = pipeline.execute_training(dataset_version_id=model_record.dataset_version_id)
            
            # Save Model Weights physically
            # Wait, the pipeline only holds it in memory right now. Let's use the registry manager to allocate a path.
            file_path = await registry_manager.register_model(db, model_id)
            pipeline.save_pipeline(file_path)
            
            # Update run with success
            await training_repo.update(
                db, 
                db_obj=run, 
                obj_in=TrainingRunUpdate(completed_at=datetime.now(timezone.utc), training_metrics=metrics)
            )
            
            logger.info(f"Training completed successfully for model {model_id}")
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            await training_repo.update(
                db, 
                db_obj=run, 
                obj_in=TrainingRunUpdate(completed_at=datetime.now(timezone.utc), error_message=str(e))
            )
            await registry_repo.update(db, db_obj=model_record, obj_in=ModelRegistryUpdate(status=ModelStatus.FAILED))


@celery_app.task(name="train_model_task", bind=True, max_retries=3)
def train_model_task(self, run_id_str: str, model_id_str: str):
    """
    Celery task wrapper for model training.
    """
    logger.info(f"Starting Celery task: train_model_task for model {model_id_str}")
    try:
        asyncio.run(async_train_model(UUID(run_id_str), UUID(model_id_str)))
        return "Training task completed"
    except Exception as exc:
        logger.error(f"Training task failed for model {model_id_str}: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
