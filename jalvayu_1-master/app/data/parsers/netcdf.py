from typing import Any, Dict
import xarray as xr
from loguru import logger

from app.data.parsers.base import BaseParser

class NetCDFParser(BaseParser):
    """
    Parser for NetCDF (.nc) files using xarray.
    """

    def parse(self, file_path: str) -> xr.Dataset:
        logger.info(f"Parsing NetCDF file: {file_path}")
        try:
            ds = xr.open_dataset(file_path, engine="netcdf4")
            return ds
        except Exception as e:
            logger.error(f"Failed to parse NetCDF file {file_path}: {e}")
            raise

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extracts key metadata without loading the entire dataset into memory.
        """
        metadata = {}
        try:
            with xr.open_dataset(file_path, engine="netcdf4") as ds:
                metadata["dimensions"] = dict(ds.dims)
                metadata["variables"] = list(ds.data_vars.keys())
                
                # Try to extract spatial bounds if lat/lon exist
                if "lat" in ds.coords and "lon" in ds.coords:
                    metadata["spatial_extent"] = {
                        "min_lat": float(ds.lat.min()),
                        "max_lat": float(ds.lat.max()),
                        "min_lon": float(ds.lon.min()),
                        "max_lon": float(ds.lon.max())
                    }
                    
                # Try to extract time bounds
                if "time" in ds.coords:
                    metadata["temporal_extent"] = {
                        "start": str(ds.time.min().values),
                        "end": str(ds.time.max().values)
                    }
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}")
            
        return metadata
