import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Enum, ForeignKey, Text, Float, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class ModelAlgorithm(str, enum.Enum):
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    RANDOM_FOREST = "random_forest"
    PROPHET = "prophet"
    LSTM = "lstm"


class ModelStatus(str, enum.Enum):
    TRAINING = "training"
    EVALUATING = "evaluating"
    READY = "ready"
    FAILED = "failed"
    DEPRECATED = "deprecated"


class ModelRegistry(Base):
    """
    Central registry for all trained Machine Learning models.
    """
    __tablename__ = "model_registry"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "v1.0.0"
    algorithm: Mapped[ModelAlgorithm] = mapped_column(Enum(ModelAlgorithm), index=True, nullable=False)
    
    # Path to serialized weights (e.g. .pkl, .h5) in the storage layer (/app/data/models/)
    model_path: Mapped[Optional[str]] = mapped_column(String(1000))
    
    # Links the model to the data it was trained on
    dataset_version_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("dataset_versions.id", ondelete="SET NULL"), index=True)
    
    status: Mapped[ModelStatus] = mapped_column(Enum(ModelStatus), default=ModelStatus.TRAINING, index=True)
    is_active_deployment: Mapped[bool] = mapped_column(default=False, index=True) # Only one active per prediction target
    target_variable: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., 'rainfall', 'temperature_max'
    
    configuration: Mapped[Optional[dict]] = mapped_column(JSONB)
    feature_set: Mapped[Optional[dict]] = mapped_column(JSONB)

    runs: Mapped[list["TrainingRun"]] = relationship(back_populates="model", cascade="all, delete-orphan")


class TrainingRun(Base):
    """
    Tracks an individual training execution for a model.
    """
    __tablename__ = "training_runs"

    model_id: Mapped[UUID] = mapped_column(ForeignKey("model_registry.id", ondelete="CASCADE"), index=True, nullable=False)
    
    started_at: Mapped[Optional[datetime]]
    completed_at: Mapped[Optional[datetime]]
    
    hyperparameters: Mapped[Optional[dict]] = mapped_column(JSONB)
    training_metrics: Mapped[Optional[dict]] = mapped_column(JSONB) # e.g. loss curves
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    model: Mapped["ModelRegistry"] = relationship(back_populates="runs")
    evaluation: Mapped[Optional["EvaluationReport"]] = relationship(back_populates="training_run", uselist=False, cascade="all, delete-orphan")


class EvaluationReport(Base):
    """
    Stores final evaluation metrics for a completed training run.
    """
    __tablename__ = "evaluation_reports"

    training_run_id: Mapped[UUID] = mapped_column(ForeignKey("training_runs.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    mae: Mapped[Optional[float]] = mapped_column(Float)
    rmse: Mapped[Optional[float]] = mapped_column(Float)
    mape: Mapped[Optional[float]] = mapped_column(Float)
    r2_score: Mapped[Optional[float]] = mapped_column(Float)
    
    residual_analysis: Mapped[Optional[dict]] = mapped_column(JSONB) # summary stats of residuals

    training_run: Mapped["TrainingRun"] = relationship(back_populates="evaluation")


class PredictionRun(Base):
    """
    Tracks a batch prediction job (e.g. generating tomorrow's rainfall map).
    """
    __tablename__ = "prediction_runs"

    model_id: Mapped[UUID] = mapped_column(ForeignKey("model_registry.id", ondelete="CASCADE"), index=True, nullable=False)
    target_date: Mapped[datetime] = mapped_column(index=True, nullable=False)
    
    started_at: Mapped[Optional[datetime]]
    completed_at: Mapped[Optional[datetime]]
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True) # pending, running, completed, failed
    
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    results: Mapped[list["PredictionResult"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class PredictionResult(Base):
    """
    Stores the output location of a batch prediction run.
    """
    __tablename__ = "prediction_results"

    run_id: Mapped[UUID] = mapped_column(ForeignKey("prediction_runs.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # Path to the resulting NetCDF/Zarr file containing the predicted grid
    output_file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    
    # Simple aggregate metrics of the prediction (e.g. max expected rainfall)
    max_value: Mapped[Optional[float]] = mapped_column(Float)
    mean_value: Mapped[Optional[float]] = mapped_column(Float)

    run: Mapped["PredictionRun"] = relationship(back_populates="results")
