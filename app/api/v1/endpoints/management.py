from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

@router.get("/datasets")
async def get_datasets():
    """
    Mock list of loaded datasets for the dashboard.
    """
    datasets = [
        {
            "id": "ds-001",
            "name": "INSAT-3D LST",
            "source": "MOSDAC ISRO",
            "variable": "Land Surface Temperature",
            "frequency": "Daily",
            "status": "processed",
            "created_at": "2026-07-01T00:00:00Z",
            "metadata": {"size_mb": 350}
        },
        {
            "id": "ds-002",
            "name": "IMD Gridded Rainfall",
            "source": "IMD Pune",
            "variable": "Rainfall",
            "frequency": "Daily",
            "status": "processed",
            "created_at": "2026-06-30T00:00:00Z",
            "metadata": {"size_mb": 150}
        }
    ]
    return {"data": datasets}

@router.get("/models/metrics")
async def get_models():
    """
    Mock list of AI models for the dashboard.
    """
    models = [
        {
            "model_name": "weather_tf_model.h5",
            "version": "1.0",
            "mae": 1.24,
            "rmse": 1.86,
            "mape": 4.5,
            "r2": 0.94,
            "last_trained": "2026-06-30T10:00:00Z"
        }
    ]
    return {"data": models}

@router.get("/models/{model_name}/history")
async def get_model_history(model_name: str):
    """
    Returns synthetic epoch validation loss data mimicking a PyTorch/TF training run.
    """
    import math
    history_data = []
    for epoch in range(10, 51, 10):
        # Generates a realistic looking exponential decay curve
        loss = 0.5 + 0.8 * math.exp(-epoch / 20.0)
        history_data.append({
            "name": f"Epoch {epoch}",
            "value": round(loss, 3)
        })
    return {"data": history_data}

