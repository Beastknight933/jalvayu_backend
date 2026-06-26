import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Enum, ForeignKey, Text, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class SimulationStatus(str, enum.Enum):
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationRun(Base):
    """
    Tracks user-triggered 'what-if' scenarios in the Digital Twin.
    """
    __tablename__ = "simulation_runs"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Configuration of the scenario (e.g., {"temp_modifier": "+2.0", "region": "Maharashtra"})
    scenario_parameters: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    status: Mapped[SimulationStatus] = mapped_column(Enum(SimulationStatus), default=SimulationStatus.PENDING, index=True)
    
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    end_date: Mapped[datetime] = mapped_column(nullable=False)
    current_timestep: Mapped[Optional[datetime]] = mapped_column()
    
    started_at: Mapped[Optional[datetime]]
    completed_at: Mapped[Optional[datetime]]
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    snapshots: Mapped[list["SimulationSnapshot"]] = relationship(back_populates="simulation", cascade="all, delete-orphan")


class SimulationSnapshot(Base):
    """
    Represents the calculated climate state at a specific timestep within a simulation.
    """
    __tablename__ = "simulation_snapshots"

    simulation_id: Mapped[UUID] = mapped_column(ForeignKey("simulation_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    
    timestep: Mapped[datetime] = mapped_column(index=True, nullable=False)
    
    # Path to the NetCDF/Zarr file holding the simulated state grid
    state_file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    
    # Aggregated metrics for quick dashboard rendering without loading the full grid
    avg_temperature: Mapped[Optional[float]] = mapped_column(Float)
    total_rainfall: Mapped[Optional[float]] = mapped_column(Float)

    simulation: Mapped["SimulationRun"] = relationship(back_populates="snapshots")


class ForecastHistory(Base):
    """
    Stores metadata and paths to standard generated forecasts (e.g., 7-day outlook).
    These are the operational forecasts for the Digital Twin.
    """
    __tablename__ = "forecast_history"

    target_variable: Mapped[str] = mapped_column(String(100), index=True, nullable=False) # e.g., 'rainfall'
    forecast_horizon_days: Mapped[int] = mapped_column(Integer, nullable=False) # e.g., 7
    
    # The date the forecast was generated
    generation_date: Mapped[datetime] = mapped_column(index=True, nullable=False)
    
    # Path to the forecasted grid sequence
    forecast_file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    
    # Link to the ML model that produced this forecast
    model_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("model_registry.id", ondelete="SET NULL"))
