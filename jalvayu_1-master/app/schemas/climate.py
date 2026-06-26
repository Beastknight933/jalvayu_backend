from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, AnyUrl

from app.models.climate import DatasetSource


# --- ClimateDataset Schemas ---
class ClimateDatasetBase(BaseModel):
    name: str
    description: Optional[str] = None
    source: DatasetSource
    source_url: Optional[str] = None
    is_active: bool = True


class ClimateDatasetCreate(ClimateDatasetBase):
    pass


class ClimateDatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    source: Optional[DatasetSource] = None
    source_url: Optional[str] = None
    is_active: Optional[bool] = None


class ClimateDatasetResponse(ClimateDatasetBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- DatasetVersion Schemas ---
class DatasetVersionBase(BaseModel):
    dataset_id: UUID
    version_tag: str
    resolution_spatial: Optional[str] = None
    resolution_temporal: Optional[str] = None


class DatasetVersionCreate(DatasetVersionBase):
    pass


class DatasetVersionResponse(DatasetVersionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
