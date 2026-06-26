from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.twin import SimulationStatus


# --- SimulationRun Schemas ---
class SimulationRunBase(BaseModel):
    name: str
    description: Optional[str] = None
    scenario_parameters: Dict[str, Any]
    start_date: datetime
    end_date: datetime


class SimulationRunCreate(SimulationRunBase):
    pass


class SimulationRunUpdate(BaseModel):
    status: Optional[SimulationStatus] = None
    current_timestep: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class SimulationRunResponse(SimulationRunBase):
    id: UUID
    status: SimulationStatus
    current_timestep: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
