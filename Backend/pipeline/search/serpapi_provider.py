import httpx
from app.config import settings
from app.core.logging import get_logger
from pipeline.search.base import BaseSearchProvider, SearchResult

logger = get_logger("serpapi_provider")


class SerpAPIProvider(BaseSearchProvider):
    """Google Images search provider utilizing SerpAPI."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or getattr(settings, "serpapi_key", None)

    def search(self, query: str) -> SearchResult:
        logger.info(f"Querying SerpAPI for: '{query}'")
        if not self.api_key:
            logger.warning(
                "SerpAPI key not configured in settings. Returning empty SearchResult."
            )
            return SearchResult()

        url = "https://serpapi.com/search.json"
        params = {
            "q": query,
            "tbm": "isch",
            "api_key": self.api_key,
            "num": 5,
        }
        try:
            response = httpx.get(url, params=params, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                images = data.get("images_results", [])
                if images:
                    first_img = images[0]
                    image_url = first_img.get("original")
                    product_url = first_img.get("link")
                    logger.info(f"Found image from SerpAPI: {image_url}")
                    return SearchResult(
                        image_url=image_url, product_url=product_url
                    )
                else:
                    logger.warning("No image results found in SerpAPI response.")
            else:
                logger.error(
                    f"SerpAPI search failed with status code: {response.status_code}"
                )
        except Exception as e:
            logger.error(f"SerpAPI request error: {e}")

        return SearchResult()
