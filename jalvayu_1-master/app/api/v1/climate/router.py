from typing import List
from uuid import UUID
import os

from fastapi import APIRouter, Request, UploadFile, File, HTTPException

from app.api.dependencies import SessionDep, CurrentUser
from app.schemas.climate import ClimateDatasetCreate, ClimateDatasetResponse, DatasetVersionCreate, DatasetVersionResponse
from app.services.climate import climate_service
from app.api.core.responses import APIResponse, APIPaginatedResponse, PaginatedData
from app.api.middlewares.rate_limit import limiter
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=APIResponse[ClimateDatasetResponse], status_code=201)
@limiter.limit("20/minute")
async def create_dataset(
    request: Request,
    db: SessionDep,
    current_user: CurrentUser,
    obj_in: ClimateDatasetCreate,
):
    """
    Register a new Climate Dataset (e.g., IMD Gridded Rainfall).
    """
    data = await climate_service.create_dataset(db, obj_in=obj_in)
    return APIResponse(success=True, data=data)

@router.get("/", response_model=APIPaginatedResponse[ClimateDatasetResponse])
@limiter.limit("100/minute")
async def list_datasets(
    request: Request,
    db: SessionDep,
    skip: int = 0,
    limit: int = 100,
):
    """
    List all available Climate Datasets.
    """
    data = await climate_service.get_datasets(db, skip=skip, limit=limit)
    paginated = PaginatedData(items=data, total=len(data), skip=skip, limit=limit)
    return APIPaginatedResponse(success=True, data=paginated)

@router.get("/{dataset_id}", response_model=APIResponse[ClimateDatasetResponse])
async def get_dataset(
    db: SessionDep,
    dataset_id: UUID,
):
    """
    Get details of a specific Climate Dataset.
    """
    data = await climate_service.get_dataset(db, id=dataset_id)
    return APIResponse(success=True, data=data)

@router.post("/versions", response_model=APIResponse[DatasetVersionResponse], status_code=201)
@limiter.limit("20/minute")
async def add_dataset_version(
    request: Request,
    db: SessionDep,
    current_user: CurrentUser,
    obj_in: DatasetVersionCreate,
):
    """
    Add a new version for an existing dataset (e.g., v1.0).
    """
    data = await climate_service.add_version(db, obj_in=obj_in)
    return APIResponse(success=True, data=data)

@router.post("/{dataset_id}/upload")
@limiter.limit("5/minute")
async def upload_dataset_file(
    request: Request,
    dataset_id: UUID,
    current_user: CurrentUser,
    file: UploadFile = File(...)
):
    """
    Upload large datasets (NetCDF, GeoTIFF) directly to the server.
    Uses chunking to stream directly to disk without consuming massive memory.
    """
    allowed_extensions = [".nc", ".nc4", ".tif", ".tiff", ".h5", ".csv"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension {ext}")
        
    # Ensure directory exists
    upload_dir = os.path.join(settings.DATA_STORAGE_BASE_PATH, "raw", "uploads", str(dataset_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    # Stream in chunks
    try:
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024 * 5) # 5MB chunks
                if not chunk:
                    break
                buffer.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
        
    return APIResponse(success=True, message="File uploaded successfully", data={"file_path": file_path})
