from fastapi import APIRouter, Depends
from app.api.dependencies import WeatherServiceDep, CurrentUser
from app.schemas.weather import WeatherRequest, WeatherResponse

router = APIRouter()

@router.post("/predict", response_model=WeatherResponse)
async def predict_weather(
    request: WeatherRequest,
    weather_service: WeatherServiceDep,
    current_user: CurrentUser
):
    """
    Get weather data (Max Temp, Min Temp, Rainfall, LST, SST) for a given location and date.
    This seamlessly uses either the local AI models or live IMD/ISRO APIs based on the backend configuration.
    """
    return await weather_service.get_weather(request)
