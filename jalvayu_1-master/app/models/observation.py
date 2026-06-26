import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Enum, ForeignKey, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.db.base import Base


class ObservationType(str, enum.Enum):
    RAINFALL = "rainfall"
    TEMPERATURE_MAX = "temperature_max"
    TEMPERATURE_MIN = "temperature_min"
    LST = "land_surface_temperature"
    SST = "sea_surface_temperature"


class ObservationMetadata(Base):
    """
    Tracks raw and processed NetCDF/Zarr files on disk containing gridded observation data.
    Does NOT store the grid points in PostGIS to avoid massive overhead.
    """
    __tablename__ = "observation_metadata"

    version_id: Mapped[str] = mapped_column(ForeignKey("dataset_versions.id", ondelete="CASCADE"), index=True, nullable=False)
    observation_type: Mapped[ObservationType] = mapped_column(Enum(ObservationType), index=True, nullable=False)
    
    # Time validity for this specific file (e.g., daily file)
    valid_time: Mapped[datetime] = mapped_column(index=True, nullable=False)
    
    # Paths in storage
    raw_file_path: Mapped[Optional[str]] = mapped_column(String(1000))
    processed_file_path: Mapped[Optional[str]] = mapped_column(String(1000))
    
    # Spatial extent for this specific observation file
    spatial_extent = mapped_column(Geometry("POLYGON", srid=4326), nullable=True)
    
    # Quick access statistics (optional, extracted during processing)
    min_value: Mapped[Optional[float]] = mapped_column(Float)
    max_value: Mapped[Optional[float]] = mapped_column(Float)
    mean_value: Mapped[Optional[float]] = mapped_column(Float)
    
    is_processed: Mapped[bool] = mapped_column(default=False, index=True)
    is_corrupted: Mapped[bool] = mapped_column(default=False)
