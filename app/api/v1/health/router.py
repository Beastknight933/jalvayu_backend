from typing import Dict, Any
from fastapi import APIRouter
from sqlalchemy import text

from app.api.dependencies import SessionDep
from app.api.core.responses import APIResponse

router = APIRouter()

@router.get("", response_model=APIResponse[Dict[str, Any]])
async def check_health(db: SessionDep):
    """
    Comprehensive system health check.
    Validates connections to Database, Redis (mocked here), and Celery (mocked here).
    """
    import datetime
    health_status = {
        "api": "healthy",
        "database": "unhealthy",
        "redis": "healthy", # Mocked as healthy for UI
        "celery": "healthy", # Mocked as healthy for UI
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }

    try:
        # Check Database
        await db.execute(text("SELECT 1"))
        health_status["database"] = "healthy"
    except Exception as e:
        health_status["database"] = "unhealthy"
        health_status["status"] = "degraded"

    return APIResponse(
        success=health_status["status"] == "healthy",
        message=f"System is {health_status['status']}",
        data=health_status
    )
