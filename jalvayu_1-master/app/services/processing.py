from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.exceptions import NotFoundException
from app.repositories.processing import job_repo
from app.schemas.processing import ProcessingJobCreate, ProcessingJobUpdate, ProcessingJobResponse
from app.models.processing import JobStatus


class ProcessingService:
    """
    Business logic for triggering and monitoring data pipelines.
    """

    async def create_job(self, db: AsyncSession, *, obj_in: ProcessingJobCreate) -> ProcessingJobResponse:
        job = await job_repo.create(db, obj_in=obj_in)
        logger.info(f"Created new processing job {job.id} of type {job.job_type}")
        return ProcessingJobResponse.model_validate(job)

    async def update_job_status(self, db: AsyncSession, *, id: UUID, status: JobStatus, error_message: str = None) -> ProcessingJobResponse:
        job = await job_repo.get(db, id=id)
        if not job:
            raise NotFoundException("Job not found")
            
        update_data = ProcessingJobUpdate(status=status)
        if error_message:
            update_data.error_message = error_message
            
        updated_job = await job_repo.update(db, db_obj=job, obj_in=update_data)
        logger.info(f"Job {updated_job.id} status updated to {updated_job.status}")
        return ProcessingJobResponse.model_validate(updated_job)
        
    async def get_job(self, db: AsyncSession, *, id: UUID) -> ProcessingJobResponse:
        job = await job_repo.get(db, id=id)
        if not job:
            raise NotFoundException("Job not found")
        return ProcessingJobResponse.model_validate(job)


processing_service = ProcessingService()
