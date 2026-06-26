import abc
from typing import Any

class BaseFeatureEngineer(abc.ABC):
    """
    Abstract Base Class for Feature Engineering.
    Calculates derived features such as anomalies, rolling averages,
    and extreme indicators (e.g., heatwaves, drought indices).
    """

    @abc.abstractmethod
    def engineer(self, data: Any) -> Any:
        """
        Applies feature engineering logic to the data.
        Returns the data object enriched with new variables/features.
        """
        pass

class RollingAverageEngineer(BaseFeatureEngineer):
    """
    Calculates moving averages over a specific time window.
    """
    def __init__(self, window_size: int = 7):
        self.window_size = window_size
        
    def engineer(self, data: Any) -> Any:
        # e.g., using xarray rolling: data.rolling(time=self.window_size).mean()
        return data

class AnomalyEngineer(BaseFeatureEngineer):
    """
    Calculates anomalies relative to a baseline climatology (e.g., 30-year average).
    """
    def __init__(self, baseline_data: Any = None):
        self.baseline_data = baseline_data
        
    def engineer(self, data: Any) -> Any:
        # Subtract the baseline climatology from the current data
        # e.g., data.groupby("time.month") - self.baseline_data
        return data
