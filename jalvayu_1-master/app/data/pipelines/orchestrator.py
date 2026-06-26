import asyncio
from uuid import UUID
from loguru import logger
from datetime import datetime

from app.models.processing import JobStatus
from app.schemas.processing import ProcessingJobUpdate
from app.repositories.processing import job_repo
from app.db.session import AsyncSessionLocal
from app.data.downloaders.imd import IMDDownloader
from app.data.validators.base import IntegrityValidator
from app.data.storage import storage


class DataIngestionPipeline:
    """
    Orchestrates the data ingestion process: Download -> Validate -> Store Metadata.
    """

    async def execute(self, job_id: UUID, url: str, dataset_source: str, file_name: str) -> None:
        async with AsyncSessionLocal() as db:
            job = await job_repo.get(db, id=job_id)
            if not job:
                logger.error(f"Job {job_id} not found. Aborting pipeline.")
                return

            try:
                # 1. Update status to DOWNLOADING
                await self._update_job_status(db, job, JobStatus.DOWNLOADING)
                
                # Setup paths
                relative_raw_path = f"{dataset_source.lower()}/{file_name}"
                
                # 2. Download
                # In a real scenario, the downloader is injected or selected via a factory
                downloader = IMDDownloader() 
                temp_path = f"/tmp/{file_name}" # Use actual tempfile logic in production
                success = await downloader.download(url, temp_path)
                
                if not success:
                    raise Exception("Download failed.")

                # 3. Update status to VALIDATING
                await self._update_job_status(db, job, JobStatus.VALIDATING)
                
                # 4. Validate
                validator = IntegrityValidator()
                is_valid, errors = validator.validate(temp_path)
                
                if not is_valid:
                    # In a real scenario, create ValidationReport entries
                    raise Exception(f"Validation failed: {errors}")
                
                # 5. Move to final raw storage via storage abstraction
                with open(temp_path, "rb") as f:
                    storage.save_file(f, relative_raw_path)
                
                # Clean up temp file (skipping actual cleanup in this mock)

                # 6. Mark as completed
                await self._update_job_status(db, job, JobStatus.COMPLETED, completed_at=datetime.utcnow())
                logger.info(f"Pipeline completed successfully for job {job_id}.")
                
            except Exception as e:
                logger.error(f"Pipeline failed for job {job_id}: {str(e)}")
                await self._update_job_status(db, job, JobStatus.FAILED, error_message=str(e), completed_at=datetime.utcnow())

    async def _update_job_status(self, db, job, status: JobStatus, error_message: str = None, completed_at: datetime = None):
        update_data = ProcessingJobUpdate(status=status)
        if error_message:
            update_data.error_message = error_message
        if completed_at:
            update_data.completed_at = completed_at
        await job_repo.update(db, db_obj=job, obj_in=update_data)


ingestion_pipeline = DataIngestionPipeline()
