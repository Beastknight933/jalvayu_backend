from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.processing import JobStatus


# --- ProcessingJob Schemas ---
class ProcessingJobBase(BaseModel):
    dataset_id: Optional[UUID] = None
    job_type: str


class ProcessingJobCreate(ProcessingJobBase):
    pass


class ProcessingJobUpdate(BaseModel):
    status: Optional[JobStatus] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    logs: Optional[Dict[str, Any]] = None


class ProcessingJobResponse(ProcessingJobBase):
    id: UUID
    status: JobStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- ValidationReport Schemas ---
class ValidationReportBase(BaseModel):
    job_id: UUID
    file_path: Optional[str] = None
    issue_type: str
    details: Optional[Dict[str, Any]] = None


class ValidationReportCreate(ValidationReportBase):
    pass


class ValidationReportResponse(ValidationReportBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
