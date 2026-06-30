import os
import joblib
import numpy as np
import tensorflow as tf
from datetime import date
from typing import Dict, List
from loguru import logger

# Suppress TensorFlow logging warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class WeatherPredictor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WeatherPredictor, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Loads the model and scaler on startup."""
        self.model_path = os.path.join(os.path.dirname(__file__), "weather_tf_model.h5")
        self.scaler_path = os.path.join(os.path.dirname(__file__), "weather_scaler.pkl")
        
        try:
            logger.info("Loading TensorFlow Weather Model...")
            # We compile=False because we only need it for inference, not training
            self.model = tf.keras.models.load_model(self.model_path, compile=False)
            logger.info("Loading Scikit-Learn Scaler...")
            self.scaler = joblib.load(self.scaler_path)
            self.is_ready = True
            logger.success("ML Models loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load ML Models: {e}")
            self.is_ready = False

    def predict_weather(self, lat: float, lon: float, target_date: date, 
                        tmax_delta: float = 0.0, tmin_delta: float = 0.0, rain_delta: float = 0.0) -> Dict[str, float]:
        """
        Predicts weather for a single point.
        Optionally applies 'what-if' perturbations.
        """
        if not self.is_ready:
            raise RuntimeError("Weather model is not loaded.")

        day_of_year = target_date.timetuple().tm_yday
        
        # Prepare input: [lat, lon, day_of_year]
        X = np.array([[lat, lon, day_of_year]])
        X_scaled = self.scaler.transform(X)
        
        # Inference
        predictions = self.model.predict(X_scaled, verbose=0)[0]
        
        # The model was trained to output: [rain, tmax, tmin]
        predicted_rain = float(predictions[0])
        predicted_tmax = float(predictions[1])
        predicted_tmin = float(predictions[2])
        
        # Apply what-if deltas
        predicted_rain = max(0.0, predicted_rain + rain_delta) # Rain can't be negative
        predicted_tmax += tmax_delta
        predicted_tmin += tmin_delta
        
        # Re-evaluate rain if tmax spikes severely (basic simulated digital twin logic)
        # e.g. Extreme heatwave dries up rain
        if tmax_delta >= 2.0:
            predicted_rain = max(0.0, predicted_rain * (1.0 - (tmax_delta * 0.1)))

        return {
            "predicted_rainfall": round(predicted_rain, 2),
            "predicted_tmax": round(predicted_tmax, 2),
            "predicted_tmin": round(predicted_tmin, 2)
        }
        
    def predict_grid(self, target_date: date, resolution: float = 0.5) -> List[Dict]:
        """
        Generates predictions for the entire Indian bounding box.
        Output format is tailored for Deck.GL ScatterplotLayer.
        Bounding Box: Lat 8N to 38N, Lon 68E to 98E
        """
        if not self.is_ready:
            raise RuntimeError("Weather model is not loaded.")

        day_of_year = target_date.timetuple().tm_yday
        
        # Generate grid points
        lats = np.arange(8.0, 38.0, resolution)
        lons = np.arange(68.0, 98.0, resolution)
        
        grid_points = []
        for lat in lats:
            for lon in lons:
                grid_points.append([lat, lon, day_of_year])
                
        X = np.array(grid_points)
        X_scaled = self.scaler.transform(X)
        
        # Batch Inference (very fast)
        predictions = self.model.predict(X_scaled, verbose=0)
        
        results = []
        for i, point in enumerate(grid_points):
            lat, lon, _ = point
            rain, tmax, tmin = predictions[i]
            
            results.append({
                "coordinates": [round(lon, 2), round(lat, 2)], # Deck.gl expects [lon, lat]
                "rainfall": round(float(rain), 2),
                "tmax": round(float(tmax), 2),
                "tmin": round(float(tmin), 2)
            })
            
        return results

# Instantiate the singleton so it loads immediately when the module is imported
weather_predictor = WeatherPredictor()
