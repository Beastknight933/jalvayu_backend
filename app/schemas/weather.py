from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

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
