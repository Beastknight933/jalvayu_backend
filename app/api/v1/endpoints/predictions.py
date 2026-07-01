from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Any
from pydantic import BaseModel
from datetime import datetime, timedelta, date
import uuid

from app.ml.inference import weather_predictor

router = APIRouter()

class PredictionModel(BaseModel):
    id: str
    model_name: str
    target_date: str
    variable: str
    value: float
    confidence: float
    status: str
    created_at: str

class PredictionResponse(BaseModel):
    data: List[PredictionModel]

def _generate_mock_prediction(date_obj: date, variable: str, value: float) -> PredictionModel:
    return PredictionModel(
        id=str(uuid.uuid4()),
        model_name="weather_tf_model.h5",
        target_date=date_obj.isoformat(),
        variable=variable,
        value=value,
        confidence=95.5,
        status="completed",
        created_at=datetime.utcnow().isoformat() + "Z"
    )

@router.get("/latest", response_model=PredictionResponse)
async def get_latest_predictions(variable: Optional[str] = None):
    """
    Get today's predictions for a default location (e.g., Delhi) to populate charts.
    """
    target = date.today()
    try:
        results = weather_predictor.predict_weather(lat=28.61, lon=77.20, target_date=target)
        
        preds = []
        if not variable or variable == "rainfall":
            preds.append(_generate_mock_prediction(target, "rainfall", results['predicted_rainfall']))
        if not variable or variable == "temperature":
            preds.append(_generate_mock_prediction(target, "tmax", results['predicted_tmax']))
            preds.append(_generate_mock_prediction(target, "tmin", results['predicted_tmin']))
            
        return {"data": preds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast", response_model=PredictionResponse)
async def get_forecast(days: int = Query(7)):
    """
    Loop the AI model `days` times to generate a multi-day forecast array.
    """
    preds = []
    base_date = date.today()
    try:
        for i in range(days):
            target = base_date + timedelta(days=i)
            # Default location: Delhi
            results = weather_predictor.predict_weather(lat=28.61, lon=77.20, target_date=target)
            preds.append(_generate_mock_prediction(target, "rainfall", results['predicted_rainfall']))
            preds.append(_generate_mock_prediction(target, "tmax", results['predicted_tmax']))
            
        return {"data": preds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare", response_model=PredictionResponse)
async def compare_predictions(id1: str, id2: str):
    """
    Dummy comparison for now.
    """
    return {"data": []}
