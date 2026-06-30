from abc import ABC, abstractmethod
from app.schemas.weather import WeatherRequest, WeatherResponse

class WeatherServiceInterface(ABC):
    """
    Base interface for all weather service providers.
    Allows easy switching between AI-predicted local models and Live APIs.
    """

    @abstractmethod
    async def get_weather(self, request: WeatherRequest) -> WeatherResponse:
        """
        Fetch or predict weather data for a given location and date.
        """
        pass
