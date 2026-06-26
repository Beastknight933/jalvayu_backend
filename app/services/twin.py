from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.schemas.twin import SimulationRunCreate, SimulationRunResponse
from app.repositories.twin import simulation_repo
from app.digital_twin.engine import twin_engine

class TwinService:
    """
    Business logic mapping API requests to the Digital Twin Engine.
    """
    
    async def get_state(self, db: AsyncSession, cache_service: Any) -> Dict[str, Any]:
        return await twin_engine.get_current_state(db, cache_service)

    async def trigger_simulation(self, db: AsyncSession, obj_in: SimulationRunCreate) -> SimulationRunResponse:
        # Create record
        sim = await simulation_repo.create(db, obj_in=obj_in)
        
        # We would dispatch a celery task here: run_simulation_task.delay(str(sim.id))
        # For now, just logging:
        logger.info(f"Triggered simulation {sim.id}")
        
        return SimulationRunResponse.model_validate(sim)

twin_service = TwinService()
