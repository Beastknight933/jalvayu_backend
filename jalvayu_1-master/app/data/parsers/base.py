import abc
from typing import Any, Dict
from pathlib import Path

class BaseParser(abc.ABC):
    """
    Abstract Base Class for Dataset Parsers.
    Parsers are responsible for reading raw files (NetCDF, GeoTIFF, etc.)
    and standardizing them into an internal format (e.g., xarray Dataset or pandas DataFrame).
    """

    @abc.abstractmethod
    def parse(self, file_path: str) -> Any:
        """
        Reads the file and returns a standardized data object (e.g., xarray.Dataset).
        """
        pass

    @abc.abstractmethod
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extracts temporal and spatial boundaries, variables, and dimensions.
        """
        pass
