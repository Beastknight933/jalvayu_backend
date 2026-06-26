from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.processing import ProcessingJob
from app.repositories.base import BaseRepository
from app.schemas.processing import ProcessingJobCreate, ProcessingJobUpdate


class ProcessingJobRepository(BaseRepository[ProcessingJob, ProcessingJobCreate, ProcessingJobUpdate]):
    async def get_active_jobs(self, db: AsyncSession) -> list[ProcessingJob]:
        query = select(ProcessingJob).where(
            ProcessingJob.status.in_(["pending", "downloading", "validating", "processing"])
        )
        result = await db.execute(query)
        return list(result.scalars().all())


job_repo = ProcessingJobRepository(ProcessingJob)
