"""Health check endpoint for load balancers and Docker."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, object]:
    """Return basic service status. Model loading comes in Task 37."""
    return {
        "status": "ok",
        "model_loaded": False,
        "catalog_count": 0,
        "model_version": "not_loaded",
    }
