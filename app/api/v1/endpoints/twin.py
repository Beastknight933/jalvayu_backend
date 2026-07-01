from fastapi import APIRouter
from typing import Dict, Any
from pydantic import BaseModel
import psutil
from datetime import datetime

router = APIRouter()

class TwinConfig(BaseModel):
    resolution: str
    cache_enabled: bool
    default_model: str

class TwinStatus(BaseModel):
    engine_state: str
    active_workers: int
    loaded_dataset: str
    memory_usage_mb: float
    last_sync: str
    config: TwinConfig

class TwinStatusResponse(BaseModel):
    data: TwinStatus

# Mock config state
current_config = TwinConfig(
    resolution="high",
    cache_enabled=True,
    default_model="weather_tf_model.h5"
)

@router.get("/status", response_model=TwinStatusResponse)
async def get_twin_status():
    """
    Returns actual system status using psutil to make the dashboard real.
    """
    process = psutil.Process()
    # Get memory usage in MB
    mem_info = process.memory_info()
    mem_mb = mem_info.rss / (1024 * 1024)
    
    status = TwinStatus(
        engine_state="active",
        active_workers=psutil.cpu_count(logical=False) or 4,
        loaded_dataset="INSAT-3D_L2B_LST_Daily",
        memory_usage_mb=round(mem_mb, 2),
        last_sync=datetime.utcnow().isoformat() + "Z",
        config=current_config
    )
    return {"data": status}

@router.patch("/config", response_model=TwinStatusResponse)
async def update_twin_config(config_updates: dict):
    global current_config
    # Update current_config with incoming values
    if "resolution" in config_updates:
        current_config.resolution = config_updates["resolution"]
    if "cache_enabled" in config_updates:
        current_config.cache_enabled = config_updates["cache_enabled"]
    if "default_model" in config_updates:
        current_config.default_model = config_updates["default_model"]
        
    return await get_twin_status()
