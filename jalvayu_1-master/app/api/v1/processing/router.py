from uuid import UUID

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.api.dependencies import SessionDep, CurrentUser
from app.schemas.processing import ProcessingJobCreate, ProcessingJobResponse
from app.services.processing import processing_service
from app.workers.tasks.data_ingestion import ingest_climate_dataset_task
from app.api.core.responses import APIResponse
from app.api.middlewares.rate_limit import limiter

router = APIRouter()

class IngestionRequest(BaseModel):
    dataset_id: UUID
    url: str
    dataset_source: str
    file_name: str


@router.post("/ingest", response_model=APIResponse[ProcessingJobResponse], status_code=202)
@limiter.limit("10/minute")
async def trigger_ingestion(
    request: Request,
    db: SessionDep,
    current_user: CurrentUser,
    payload: IngestionRequest,
):
    """
    Triggers an asynchronous data ingestion pipeline.
    Creates a ProcessingJob in the DB and pushes a task to Celery.
    """
    job_in = ProcessingJobCreate(
        dataset_id=payload.dataset_id,
        job_type=f"INGESTION_{payload.dataset_source}"
    )
    job = await processing_service.create_job(db, obj_in=job_in)
    
    ingest_climate_dataset_task.delay(
        str(job.id),
        payload.url,
        payload.dataset_source,
        payload.file_name
    )
    
    return APIResponse(success=True, message="Ingestion task scheduled", data=job)


@router.get("/jobs/{job_id}", response_model=APIResponse[ProcessingJobResponse])
async def get_job_status(
    db: SessionDep,
    job_id: UUID,
):
    """
    Get the current status of a processing job.
    """
    data = await processing_service.get_job(db, id=job_id)
    return APIResponse(success=True, data=data)
