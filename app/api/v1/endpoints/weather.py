from fastapi import APIRouter, HTTPException
from typing import List, Any
from datetime import date
from app.schemas.weather import WeatherPredictionRequest, WeatherPredictionResponse, SimulationRequest
from app.ml.inference import weather_predictor

router = APIRouter()

@router.post("/predict", response_model=WeatherPredictionResponse)
async def predict_weather(request: WeatherPredictionRequest) -> Any:
    """
    Get a short-term weather prediction for a specific latitude and longitude.
    """
    try:
        results = weather_predictor.predict_weather(
            lat=request.latitude,
            lon=request.longitude,
            target_date=request.target_date
        )
        return WeatherPredictionResponse(
            latitude=request.latitude,
            longitude=request.longitude,
            target_date=request.target_date,
            **results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate", response_model=WeatherPredictionResponse)
async def simulate_weather(request: SimulationRequest) -> Any:
    """
    Digital Twin 'What-If' Simulation:
    Pass in perturbations (e.g. tmax_delta=+2.0) to see how climate changes impact the region.
    """
    try:
        results = weather_predictor.predict_weather(
            lat=request.latitude,
            lon=request.longitude,
            target_date=request.target_date,
            tmax_delta=request.tmax_delta,
            tmin_delta=request.tmin_delta,
            rain_delta=request.rainfall_delta
        )
        return WeatherPredictionResponse(
            latitude=request.latitude,
            longitude=request.longitude,
            target_date=request.target_date,
            **results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/grid")
async def get_weather_grid(target_date: date, resolution: float = 0.5) -> Any:
    """
    Generates a geospatial grid of predictions over the Pilot Region (India).
    Returns a JSON array formatted for direct ingestion into Deck.gl ScatterplotLayer.
    """
    try:
        # Cap resolution to avoid OOM errors
        if resolution < 0.25:
            resolution = 0.25
            
        grid_data = weather_predictor.predict_grid(
            target_date=target_date, 
            resolution=resolution
        )
        return grid_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
