import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    VALIDATING = "validating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingJob(Base):
    """
    Tracks the state of a data pipeline job (Download -> Validate -> Process -> Load).
    """
    __tablename__ = "processing_jobs"

    dataset_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("climate_datasets.id", ondelete="SET NULL"), index=True)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., 'IMD_RAINFALL_INGESTION'
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING, index=True, nullable=False)
    
    started_at: Mapped[Optional[datetime]]
    completed_at: Mapped[Optional[datetime]]
    
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    logs: Mapped[Optional[dict]] = mapped_column(JSONB) # Structured logs


class ValidationReport(Base):
    """
    Stores reports for corrupted files, missing timestamps, outliers, etc.
    """
    __tablename__ = "validation_reports"

    job_id: Mapped[UUID] = mapped_column(ForeignKey("processing_jobs.id", ondelete="CASCADE"), index=True, nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(1000))
    issue_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., 'CORRUPTED_FILE', 'MISSING_COORDINATES'
    details: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    job: Mapped["ProcessingJob"] = relationship()


class ImportHistory(Base):
    """
    Audit log of successful imports into the system.
    """
    __tablename__ = "import_history"

    version_id: Mapped[UUID] = mapped_column(ForeignKey("dataset_versions.id", ondelete="CASCADE"), index=True, nullable=False)
    job_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("processing_jobs.id", ondelete="SET NULL"))
    
    files_processed: Mapped[int] = mapped_column(default=0)
    data_points_added: Mapped[Optional[int]] = mapped_column(default=0) # Informational
    import_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
