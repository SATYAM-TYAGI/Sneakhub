from abc import ABC, abstractmethod
from typing import Optional


class SearchResult:
    """Dataclass holding search result attributes (image URL and product link)."""

    def __init__(self, image_url: Optional[str] = None, product_url: Optional[str] = None):
        self.image_url = image_url
        self.product_url = product_url


class BaseSearchProvider(ABC):
    """Abstract base class representing a search provider plugin."""

    @abstractmethod
    def search(self, query: str) -> SearchResult:
        """Execute the search query and return a SearchResult."""
        pass
