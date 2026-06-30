from app.schemas.weather import WeatherRequest, WeatherResponse
from app.services.weather_base import WeatherServiceInterface

class LiveWeatherService(WeatherServiceInterface):
    """
    Live API Service (Placeholder for future IMD/ISRO Integration).
    This service will eventually make HTTP calls to the real APIs.
    """

    async def get_weather(self, request: WeatherRequest) -> WeatherResponse:
        # TODO: Implement HTTP calls to IMD / ISRO Bhuvan APIs here once access is granted.
        raise NotImplementedError("Live API access is not currently available. Please use AIWeatherPredictionService.")
