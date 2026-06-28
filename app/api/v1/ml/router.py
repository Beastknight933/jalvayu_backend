from typing import List
from uuid import UUID

from fastapi import APIRouter, Request

from app.api.dependencies import SessionDep, CurrentUser
from app.schemas.ml import ModelRegistryCreate, ModelRegistryResponse, TrainingRunResponse
from app.services.ml import ml_service
from app.api.core.responses import APIResponse, APIPaginatedResponse, PaginatedData
from app.api.middlewares.rate_limit import limiter

router = APIRouter()

@router.post("/models", response_model=APIResponse[ModelRegistryResponse], status_code=201)
@limiter.limit("10/minute")
async def register_model(
    request: Request,
    db: SessionDep,
    current_user: CurrentUser,
    obj_in: ModelRegistryCreate
):
    """
    Register a new ML model configuration to the registry.
    """
    data = await ml_service.register_model(db, obj_in=obj_in)
    return APIResponse(success=True, data=data)

@router.get("/models", response_model=APIPaginatedResponse[ModelRegistryResponse])
async def list_models(
    db: SessionDep,
    skip: int = 0,
    limit: int = 100
):
    """
    List registered ML models.
    """
    data, total = await ml_service.list_models(db, skip=skip, limit=limit)
    paginated = PaginatedData(items=data, total=total, skip=skip, limit=limit)
    return APIPaginatedResponse(success=True, data=paginated)

@router.post("/models/{model_id}/train", response_model=APIResponse[TrainingRunResponse], status_code=202)
@limiter.limit("5/minute")
async def train_model(
    request: Request,
    db: SessionDep,
    current_user: CurrentUser,
    model_id: UUID
):
    """
    Trigger an asynchronous training job for a registered model.
    """
    data = await ml_service.trigger_training(db, model_id=model_id)
    return APIResponse(success=True, message="Training job triggered asynchronously", data=data)
