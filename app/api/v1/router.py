from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router
from app.api.v1.climate.router import router as climate_router
from app.api.v1.processing.router import router as processing_router
from app.api.v1.ml.router import router as ml_router
from app.api.v1.twin.router import router as twin_router
from app.api.v1.health.router import router as health_router
from app.api.v1.metrics.router import router as metrics_router
from app.api.websockets.router import router as ws_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["system"])
api_router.include_router(metrics_router, prefix="/metrics", tags=["system"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(climate_router, prefix="/climate", tags=["climate"])
api_router.include_router(processing_router, prefix="/processing", tags=["processing"])
api_router.include_router(ml_router, prefix="/ml", tags=["machine_learning"])
api_router.include_router(twin_router, prefix="/twin", tags=["digital_twin"])
api_router.include_router(ws_router, tags=["websockets"])
# Other routers (climate data, digital twin, ML) will be included here later
