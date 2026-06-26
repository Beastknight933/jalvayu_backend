import asyncio
from uuid import UUID
from loguru import logger

from app.workers.celery_app import celery_app
from app.data.pipelines.orchestrator import ingestion_pipeline


@celery_app.task(name="ingest_climate_dataset")
def ingest_climate_dataset_task(job_id_str: str, url: str, dataset_source: str, file_name: str) -> str:
    """
    Celery task to run the ingestion pipeline.
    Celery tasks are synchronous by default, so we run the async pipeline using asyncio.run.
    """
    logger.info(f"Starting Celery task: ingest_climate_dataset for job {job_id_str}")
    job_id = UUID(job_id_str)
    
    # Run the async orchestrator
    asyncio.run(ingestion_pipeline.execute(job_id, url, dataset_source, file_name))
    
    return f"Ingestion triggered for job {job_id_str}"
