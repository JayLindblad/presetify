"""Download images from URLs."""

import tempfile
from pathlib import Path
from typing import Optional
import httpx


class ImageFetcher:
    """Download images from URLs and save to temporary files."""

    def __init__(self, timeout: int = 30):
        """
        Initialize the image fetcher.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    async def fetch(self, url: str) -> Optional[Path]:
        """
        Download an image from a URL to a temporary file.

        Args:
            url: URL of the image to download

        Returns:
            Path to the temporary file, or None if download failed
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                # Determine file extension from content-type or URL
                content_type = response.headers.get("content-type", "")
                extension = self._get_extension_from_content_type(content_type)

                if not extension:
                    # Try to get from URL
                    extension = Path(url).suffix or ".jpg"

                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix=extension, prefix="presetify_"
                )
                temp_path = Path(temp_file.name)

                # Write content
                temp_path.write_bytes(response.content)

                return temp_path

        except httpx.HTTPError as e:
            print(f"HTTP error downloading {url}: {e}")
            return None
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return None

    def _get_extension_from_content_type(self, content_type: str) -> str:
        """Get file extension from HTTP content-type header."""
        content_type = content_type.lower()

        mappings = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/tiff": ".tif",
            "image/x-adobe-dng": ".dng",
        }

        for mime, ext in mappings.items():
            if mime in content_type:
                return ext

        return ""
