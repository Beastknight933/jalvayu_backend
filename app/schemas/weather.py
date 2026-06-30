from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

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
