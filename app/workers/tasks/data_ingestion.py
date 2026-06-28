import asyncio
from uuid import UUID
from loguru import logger

from app.workers.celery_app import celery_app
from app.data.pipelines.orchestrator import ingestion_pipeline


@celery_app.task(name="ingest_climate_dataset", bind=True, max_retries=3)
def ingest_climate_dataset_task(self, job_id_str: str, url: str, dataset_source: str, file_name: str) -> str:
    """
    Celery task to run the ingestion pipeline.
    Celery tasks are synchronous by default, so we run the async pipeline using asyncio.run.
    """
    logger.info(f"Starting Celery task: ingest_climate_dataset for job {job_id_str}")
    job_id = UUID(job_id_str)
    
    try:
        # Run the async orchestrator
        asyncio.run(ingestion_pipeline.execute(job_id, url, dataset_source, file_name))
        return f"Ingestion completed for job {job_id_str}"
    except Exception as exc:
        logger.error(f"Ingestion failed for job {job_id_str}: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
