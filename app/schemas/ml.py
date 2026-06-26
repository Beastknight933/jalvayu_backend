from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.ml import ModelAlgorithm, ModelStatus


# --- ModelRegistry Schemas ---
class ModelRegistryBase(BaseModel):
    name: str
    version: str
    algorithm: ModelAlgorithm
    dataset_version_id: Optional[UUID] = None
    target_variable: str
    configuration: Optional[Dict[str, Any]] = None
    feature_set: Optional[Dict[str, Any]] = None


class ModelRegistryCreate(ModelRegistryBase):
    pass


class ModelRegistryUpdate(BaseModel):
    status: Optional[ModelStatus] = None
    is_active_deployment: Optional[bool] = None
    model_path: Optional[str] = None


class ModelRegistryResponse(ModelRegistryBase):
    id: UUID
    status: ModelStatus
    is_active_deployment: bool
    model_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- TrainingRun Schemas ---
class TrainingRunBase(BaseModel):
    model_id: UUID
    hyperparameters: Optional[Dict[str, Any]] = None


class TrainingRunCreate(TrainingRunBase):
    pass


class TrainingRunUpdate(BaseModel):
    completed_at: Optional[datetime] = None
    training_metrics: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class TrainingRunResponse(TrainingRunBase):
    id: UUID
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    training_metrics: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
