import enum
from typing import Optional

from sqlalchemy import String, Enum, ForeignKey, Text, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.db.base import Base


class DatasetSource(str, enum.Enum):
    IMD = "IMD"
    MOSDAC = "MOSDAC"
    INSAT = "INSAT"
    OTHER = "OTHER"


class ClimateDataset(Base):
    """
    High-level entity representing a national climate dataset.
    """
    __tablename__ = "climate_datasets"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[DatasetSource] = mapped_column(Enum(DatasetSource), index=True, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(default=True)

    versions: Mapped[list["DatasetVersion"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")


class DatasetVersion(Base):
    """
    Represents a specific version of a dataset (e.g., v1.0, daily, monthly).
    """
    __tablename__ = "dataset_versions"

    dataset_id: Mapped[str] = mapped_column(ForeignKey("climate_datasets.id", ondelete="CASCADE"), index=True, nullable=False)
    version_tag: Mapped[str] = mapped_column(String(50), nullable=False)
    resolution_spatial: Mapped[Optional[str]] = mapped_column(String(50)) # e.g., '0.25x0.25 deg'
    resolution_temporal: Mapped[Optional[str]] = mapped_column(String(50)) # e.g., 'daily'
    
    dataset: Mapped["ClimateDataset"] = relationship(back_populates="versions")
    metadata_records: Mapped[list["ClimateMetadata"]] = relationship(back_populates="version", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("dataset_id", "version_tag", name="uq_dataset_version"),
    )

class ClimateMetadata(Base):
    """
    Stores metadata and spatial extents for a specific dataset version.
    """
    __tablename__ = "climate_metadata"

    version_id: Mapped[str] = mapped_column(ForeignKey("dataset_versions.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # Store the bounding box of the dataset as a PostGIS Geometry (Polygon)
    spatial_extent = mapped_column(Geometry("POLYGON", srid=4326), nullable=True)
    
    temporal_coverage_start = mapped_column(String(50), nullable=True) # e.g., "1901-01-01"
    temporal_coverage_end = mapped_column(String(50), nullable=True)
    
    __table_args__ = (
        Index("ix_climate_metadata_version_temporal", "version_id", "temporal_coverage_start"),
    )
    
    variables: Mapped[Optional[str]] = mapped_column(String(500)) # Comma separated, e.g., "rainfall,tmax,tmin"
    
    version: Mapped["DatasetVersion"] = relationship(back_populates="metadata_records")
