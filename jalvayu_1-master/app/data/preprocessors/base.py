import abc
from typing import Any

class BasePreprocessor(abc.ABC):
    """
    Abstract Base Class for Preprocessors.
    Handles operations like filling missing values, standardization,
    coordinate transformation, and spatial/temporal alignment.
    """

    @abc.abstractmethod
    def process(self, data: Any) -> Any:
        """
        Applies preprocessing logic to the standardized data object.
        """
        pass


class MissingValueImputer(BasePreprocessor):
    """
    Fills missing values (e.g., NaN) using specified methods (e.g., linear interpolation).
    """
    def __init__(self, method: str = "linear"):
        self.method = method
        
    def process(self, data: Any) -> Any:
        # e.g., data.interpolate_na(dim='time', method=self.method)
        return data


class SpatialAligner(BasePreprocessor):
    """
    Aligns gridded data to a standard spatial resolution (e.g., 0.25x0.25).
    """
    def __init__(self, target_resolution: float = 0.25):
        self.target_resolution = target_resolution
        
    def process(self, data: Any) -> Any:
        # e.g., using xarray's interp() or rioxarray's reproject()
        return data
