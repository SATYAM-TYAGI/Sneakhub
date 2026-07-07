from app.core.logging import get_logger
from pipeline.search.base import BaseSearchProvider, SearchResult

logger = get_logger("manual_provider")


class ManualProvider(BaseSearchProvider):
    """Manual search provider representing preset user placeholders."""

    def search(self, query: str) -> SearchResult:
        logger.info(f"Querying ManualProvider for: '{query}'")

        # Static placeholder
        image_url = "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop"
        product_url = "https://example.com/manual-sneaker"

        return SearchResult(image_url=image_url, product_url=product_url)
