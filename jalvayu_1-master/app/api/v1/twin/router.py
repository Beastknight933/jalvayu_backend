from typing import Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.api.dependencies import SessionDep, CurrentUser
from app.schemas.twin import SimulationRunCreate, SimulationRunResponse
from app.services.twin import twin_service
from app.api.core.responses import APIResponse
from app.api.middlewares.rate_limit import limiter

# For cache injection (mocked dependency here)
async def get_cache_service():
    from app.core.redis import redis_client # Assuming configured
    from app.digital_twin.cache.service import TwinCacheService
    return TwinCacheService(redis_client)

router = APIRouter()

@router.get("/state", response_model=APIResponse[Dict[str, Any]])
@limiter.limit("60/minute")
async def get_current_twin_state(
    request: Request,
    db: SessionDep,
    cache_service = Depends(get_cache_service)
):
    """
    Get the absolute latest climate state from the Digital Twin.
    Leverages Redis cache for instant dashboard loading.
    """
    data = await twin_service.get_state(db, cache_service)
    return APIResponse(success=True, data=data)

@router.post("/simulate", response_model=APIResponse[SimulationRunResponse], status_code=202)
@limiter.limit("5/minute")
async def start_scenario_simulation(
    request: Request,
    db: SessionDep,
    current_user: CurrentUser,
    obj_in: SimulationRunCreate
):
    """
    Trigger a 'what-if' scenario simulation asynchronously.
    """
    data = await twin_service.trigger_simulation(db, obj_in=obj_in)
    return APIResponse(success=True, message="Simulation started asynchronously", data=data)
