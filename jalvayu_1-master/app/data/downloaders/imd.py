import httpx
from loguru import logger

from app.core.config import settings
from app.data.downloaders.base import BaseDownloader

class IMDDownloader(BaseDownloader):
    """
    Downloader specific to the India Meteorological Department (IMD) Gridded Data.
    Handles IMD authentication or API keys if needed in the future.
    """

    def __init__(self):
        super().__init__()
        self.api_url = settings.IMD_API_URL
        self.api_key = settings.IMD_API_KEY

    async def _fetch(self, url: str, destination_path: str, **kwargs) -> bool:
        """
        Fetch logic tailored for IMD (e.g., setting specific headers).
        """
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            # Note: The actual IMD data site might use FTP or direct links.
            # This represents an HTTP implementation.
            async with client.stream("GET", url, headers=headers) as response:
                response.raise_for_status()
                with open(destination_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
        return True
