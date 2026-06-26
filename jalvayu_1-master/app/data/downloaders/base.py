import abc
import asyncio
from typing import Optional
from pathlib import Path

from loguru import logger

class BaseDownloader(abc.ABC):
    """
    Abstract Base Class for downloading climate datasets.
    Provides hooks for retries, progress reporting, and checksum validation.
    """

    def __init__(self, max_retries: int = 3, timeout_seconds: int = 60):
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

    @abc.abstractmethod
    async def _fetch(self, url: str, destination_path: str, **kwargs) -> bool:
        """
        Implementation-specific fetch logic (e.g., HTTP GET, FTP, API SDK).
        """
        pass

    async def download(self, url: str, destination_path: str, expected_checksum: Optional[str] = None, **kwargs) -> bool:
        """
        Download a file with retry logic and optional checksum validation.
        """
        attempt = 0
        while attempt < self.max_retries:
            try:
                logger.info(f"Downloading {url} to {destination_path} (Attempt {attempt + 1}/{self.max_retries})")
                success = await self._fetch(url, destination_path, **kwargs)
                
                if success:
                    if expected_checksum:
                        # Validation logic here (mocked for now)
                        if not self.verify_checksum(destination_path, expected_checksum):
                            logger.error("Checksum validation failed.")
                            attempt += 1
                            continue
                    
                    logger.info(f"Successfully downloaded {url}")
                    return True
            except Exception as e:
                logger.error(f"Download failed: {e}")
                
            attempt += 1
            await asyncio.sleep(2 ** attempt) # Exponential backoff
            
        logger.error(f"Failed to download {url} after {self.max_retries} attempts.")
        return False

    def verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        """Verify file integrity using MD5/SHA256 (abstracted)."""
        import hashlib
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest() == expected_checksum
