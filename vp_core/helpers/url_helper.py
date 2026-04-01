from io import BytesIO

import httpx

from vp_core.logging.logger import setup_logger

logger = setup_logger()


async def download_from_url(url: str, timeout: int = 10) -> tuple[BytesIO | None, str | None]:
    """
    Downloads a file from a URL asynchronously and returns a tuple of
    (BytesIO object, content_type).
    Returns (None, None) if the download fails.
    Uses HTTP/2 for better performance.
    """
    try:
        async with httpx.AsyncClient(http2=True) as client:
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()
            return BytesIO(response.content), response.headers.get("Content-Type")
    except Exception as e:
        logger.error(f"Error downloading from {url}: {e}")
        return None, None
