"""Pydantic schemas for the sneaker recommendation requests and responses."""

from typing import List, Optional
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Pydantic model representing user preference inputs for recommendations."""

    brand: str = Field(..., description="Preferred sneaker brand name", example="Nike")
    category: str = Field(..., description="Preferred category name", example="Running")
    gender: str = Field(..., description="Target gender (men, women, unisex)", example="men")
    color: str = Field(..., description="Preferred sneaker color", example="White")
    material: str = Field(..., description="Preferred sneaker material", example="Mesh")
    budget: float = Field(..., description="Maximum budget in USD", example=120.0)


class RecommendationResponse(BaseModel):
    """Pydantic model representing a returned recommended sneaker result."""

    id: int = Field(..., description="Sneaker ID")
    display_name: str = Field(..., description="Formatted brand and model display name")
    brand: str = Field(..., description="Sneaker brand name")
    category: str = Field(..., description="Sneaker category name")
    price: float = Field(..., description="Sneaker price in USD")
    image_url: Optional[str] = Field(None, description="Cloudinary or search source image URL")
    description: Optional[str] = Field(None, description="Detailed product description")
    predicted_score: float = Field(..., description="ML model compatibility prediction score")
    explanations: List[str] = Field(..., description="Rule-based tags explaining compatibility reasons")
