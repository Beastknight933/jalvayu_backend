from app.schemas.weather import WeatherRequest, WeatherResponse
from app.services.weather_base import WeatherServiceInterface
import random

class AIWeatherPredictionService(WeatherServiceInterface):
    """
    Local AI Model Service (Zero-Cost).
    This service loads lightweight ML models (e.g., ONNX, Scikit-Learn) directly into the backend
    to generate predictions without querying any external APIs.
    """

    def __init__(self):
        # TODO: Load the actual trained Colab models here from app/ml/models/
        # e.g., self.model = joblib.load("app/ml/models/weather_model.pkl")
        self.is_loaded = True

    async def get_weather(self, request: WeatherRequest) -> WeatherResponse:
        # TODO: Replace this mock implementation with actual model inference
        # e.g., predictions = self.model.predict([[request.latitude, request.longitude, request.target_date.toordinal()]])
        
        # Mocking the AI prediction output based on location
        mock_rainfall = max(0.0, random.uniform(0, 50) + (request.latitude / 90))
        mock_max_temp = random.uniform(25, 45)
        mock_min_temp = mock_max_temp - random.uniform(5, 15)
        mock_lst = mock_max_temp + random.uniform(2, 5)
        mock_sst = mock_max_temp - random.uniform(1, 4)

        return WeatherResponse(
            latitude=request.latitude,
            longitude=request.longitude,
            target_date=request.target_date,
            max_temperature=round(mock_max_temp, 2),
            min_temperature=round(mock_min_temp, 2),
            rainfall=round(mock_rainfall, 2),
            insat_lst=round(mock_lst, 2),
            insat_sst=round(mock_sst, 2),
            source="AI_PREDICTION_LOCAL"
        )
