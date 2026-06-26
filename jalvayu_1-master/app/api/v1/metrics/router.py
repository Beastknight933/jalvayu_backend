import psutil
from typing import Dict, Any
from fastapi import APIRouter

from app.api.core.responses import APIResponse
from app.api.dependencies import CurrentUser

router = APIRouter()

@router.get("", response_model=APIResponse[Dict[str, Any]])
async def get_system_metrics(current_user: CurrentUser):
    """
    Exposes system-level metrics (CPU, Memory, API latency stats).
    Protected route - requires authentication.
    """
    metrics = {
        "cpu_usage_percent": psutil.cpu_percent(interval=1),
        "memory_usage_percent": psutil.virtual_memory().percent,
        "active_tasks": 0, # Placeholder for celery task queue size
    }
    
    return APIResponse(
        success=True,
        message="Metrics retrieved successfully",
        data=metrics
    )
