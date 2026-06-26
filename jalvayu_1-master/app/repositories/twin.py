from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.twin import SimulationRun
from app.repositories.base import BaseRepository
from app.schemas.twin import SimulationRunCreate, SimulationRunUpdate


class SimulationRunRepository(BaseRepository[SimulationRun, SimulationRunCreate, SimulationRunUpdate]):
    pass


simulation_repo = SimulationRunRepository(SimulationRun)
