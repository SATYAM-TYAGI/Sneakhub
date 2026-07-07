from app.core.logging import get_logger
from pipeline.search.base import BaseSearchProvider, SearchResult

logger = get_logger("stockx_provider")


class StockXProvider(BaseSearchProvider):
    """Mock StockX search provider returning consistent placeholder outputs."""

    def search(self, query: str) -> SearchResult:
        logger.info(f"Mocking StockX query for: '{query}'")

        # Stable hashing based on query input
        query_hash = sum(ord(char) for char in query)
        placeholders = [
            "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop",
        ]
        image_url = placeholders[query_hash % len(placeholders)]
        product_url = f"https://stockx.com/search?s={query.replace(' ', '+')}"

        return SearchResult(image_url=image_url, product_url=product_url)
