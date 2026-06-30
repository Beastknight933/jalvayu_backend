from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

# Original Schemas
class WeatherRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of the location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of the location")
    target_date: date = Field(..., description="Date for the weather prediction")

class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    target_date: date
    max_temperature: Optional[float] = Field(None, description="Maximum temperature in Celsius")
    min_temperature: Optional[float] = Field(None, description="Minimum temperature in Celsius")
    rainfall: Optional[float] = Field(None, description="Rainfall in mm")
    insat_lst: Optional[float] = Field(None, description="Land Surface Temperature from INSAT")
    insat_sst: Optional[float] = Field(None, description="Sea Surface Temperature from INSAT")
    source: str = Field(..., description="Source of the data (e.g., 'IMD_API', 'AI_PREDICTION')")

# New ML Prediction Schemas
class WeatherPredictionRequest(BaseModel):
    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    target_date: date = Field(..., description="The date to predict the weather for (YYYY-MM-DD)")

class WeatherPredictionResponse(BaseModel):
    latitude: float
    longitude: float
    target_date: date
    predicted_rainfall: float = Field(..., description="Predicted rainfall in mm")
    predicted_tmax: float = Field(..., description="Predicted max temperature in Celsius")
    predicted_tmin: float = Field(..., description="Predicted min temperature in Celsius")

class SimulationRequest(BaseModel):
    latitude: float
    longitude: float
    target_date: date
    tmax_delta: Optional[float] = Field(0.0, description="Perturbation to apply to Max Temp for what-if scenario")
    tmin_delta: Optional[float] = Field(0.0, description="Perturbation to apply to Min Temp for what-if scenario")
    rainfall_delta: Optional[float] = Field(0.0, description="Perturbation to apply to Rainfall for what-if scenario")
