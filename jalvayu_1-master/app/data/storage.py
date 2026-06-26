import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, List

from loguru import logger

from app.core.config import settings


class BaseStorage(ABC):
    """
    Abstract Base Class for Data Storage.
    Defines the contract for reading/writing raw and processed climate datasets.
    """

    @abstractmethod
    def save_file(self, file_obj: BinaryIO, relative_path: str) -> str:
        """Saves a file-like object and returns the full path/URI."""
        pass

    @abstractmethod
    def read_file(self, relative_path: str) -> BinaryIO:
        """Reads a file and returns a file-like object."""
        pass

    @abstractmethod
    def delete_file(self, relative_path: str) -> bool:
        """Deletes a file."""
        pass

    @abstractmethod
    def list_files(self, relative_dir: str) -> List[str]:
        """Lists files in a given directory."""
        pass

    @abstractmethod
    def file_exists(self, relative_path: str) -> bool:
        """Checks if a file exists."""
        pass


class LocalDiskStorage(BaseStorage):
    """
    Local Disk implementation of the storage interface.
    """

    def __init__(self, base_path: str = settings.DATA_STORAGE_BASE_PATH):
        self.base_path = Path(base_path)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.base_path / settings.DATA_RAW_DIR,
            self.base_path / settings.DATA_PROCESSED_DIR,
            self.base_path / settings.DATA_MODELS_DIR,
            self.base_path / settings.DATA_SIMULATIONS_DIR,
            self.base_path / settings.DATA_CACHE_DIR,
            self.base_path / settings.DATA_EXPORTS_DIR,
        ]
        for d in directories:
            d.mkdir(parents=True, exist_ok=True)

    def _get_full_path(self, relative_path: str) -> Path:
        return self.base_path / relative_path

    def save_file(self, file_obj: BinaryIO, relative_path: str) -> str:
        full_path = self._get_full_path(relative_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, "wb") as out_file:
            shutil.copyfileobj(file_obj, out_file)
            
        logger.info(f"Saved file to local storage: {full_path}")
        return str(full_path)

    def read_file(self, relative_path: str) -> BinaryIO:
        full_path = self._get_full_path(relative_path)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
            
        return open(full_path, "rb")

    def delete_file(self, relative_path: str) -> bool:
        full_path = self._get_full_path(relative_path)
        if full_path.exists():
            full_path.unlink()
            logger.info(f"Deleted file: {full_path}")
            return True
        return False

    def list_files(self, relative_dir: str) -> List[str]:
        full_dir = self._get_full_path(relative_dir)
        if not full_dir.exists() or not full_dir.is_dir():
            return []
        
        return [str(p.relative_to(self.base_path)) for p in full_dir.rglob("*") if p.is_file()]

    def file_exists(self, relative_path: str) -> bool:
        return self._get_full_path(relative_path).exists()


def get_storage() -> BaseStorage:
    """
    Factory function to get the configured storage backend.
    """
    if settings.STORAGE_BACKEND == "s3":
        raise NotImplementedError("S3 storage backend is not yet implemented.")
    else:
        return LocalDiskStorage()

storage = get_storage()
