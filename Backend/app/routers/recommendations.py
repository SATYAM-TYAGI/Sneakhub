"""Router endpoint for generating sneaker recommendations based on user preferences."""

from typing import List
import os
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.brand import Brand
from app.models.category import Category
from app.models.sneaker import Sneaker
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from ml.features import calculate_compatibility_score, extract_pairwise_features

import traceback
from app.core.logging import get_logger

logger = get_logger("recommendations")

router = APIRouter()


class UserPreferenceSneaker:
    """Mock sneaker object representing user preferences to match features.py interface."""

    def __init__(
        self,
        brand_id: int,
        category_id: int,
        gender: str,
        color: str,
        material: str,
        price_usd: float,
    ):
        self.brand_id = brand_id
        self.category_id = category_id
        self.gender = gender
        self.color = color
        self.material = material
        self.price_usd = price_usd


@router.post(
    "/api/recommend", response_model=List[RecommendationResponse]
)
def get_recommendations(req: RecommendationRequest, db: Session = Depends(get_db)):
    """Accepts user preferences and returns the Top 5 sneaker recommendations.

    Predictions are run through the trained RandomForest model loaded on startup.
    """
    try:
        # 1. Load active sneakers from PostgreSQL database
        try:
            sneakers = (
                db.query(Sneaker)
                .options(joinedload(Sneaker.brand), joinedload(Sneaker.category))
                .filter(Sneaker.is_active == True)
                .all()
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Database query failed: {e}"
            )

        if not sneakers:
            return []

        # 2. Resolve preferred Brand and Category IDs from DB mappings
        brand_db = (
            db.query(Brand).filter(Brand.name.ilike(req.brand.strip())).first()
        )
        category_db = (
            db.query(Category)
            .filter(Category.name.ilike(req.category.strip()))
            .first()
        )

        brand_id = brand_db.id if brand_db else -1
        category_id = category_db.id if category_db else -1

        # 3. Represent user preference inputs as baseline comparison mock sneaker
        user_pref = UserPreferenceSneaker(
            brand_id=brand_id,
            category_id=category_id,
            gender=req.gender,
            color=req.color,
            material=req.material,
            price_usd=req.budget,
        )

        # Import globally loaded ML model from main module
        from app.main import ml_model

        model = ml_model.get("model")

        recommendations = []

        for sneaker in sneakers:
            # Extract features between user preference and candidate sneaker
            feats = extract_pairwise_features(user_pref, sneaker)

            # Predict score
            if model is not None:
                # Predict using Random Forest
                X_pred = pd.DataFrame(
                    [feats],
                    columns=[
                        "brand_match",
                        "category_match",
                        "gender_match",
                        "color_match",
                        "material_match",
                        "abs_price_diff",
                    ],
                )
                score = float(model.predict(X_pred)[0])
            else:
                # Fallback to direct math scoring if model file is missing
                score = calculate_compatibility_score(user_pref, sneaker)

            # Generate rule-based explanations for matches
            explanations = []
            if sneaker.brand.name.lower() == req.brand.lower().strip():
                explanations.append("Same Brand")
            if sneaker.category.name.lower() == req.category.lower().strip():
                explanations.append("Same Category")
            if float(sneaker.price_usd) <= req.budget:
                explanations.append("Within Budget")
            if sneaker.gender.lower() == req.gender.lower().strip():
                explanations.append("Same Gender")
            if sneaker.color.lower() == req.color.lower().strip():
                explanations.append("Matching Color")
            if sneaker.material.lower() == req.material.lower().strip():
                explanations.append("Matching Material")

            recommendations.append(
                {
                    "id": sneaker.id,
                    "display_name": sneaker.display_name,
                    "brand": sneaker.brand.name,
                    "category": sneaker.category.name,
                    "price": float(sneaker.price_usd),
                    "image_url": sneaker.image_url,
                    "description": sneaker.description,
                    "predicted_score": round(score, 2),
                    "explanations": explanations,
                }
            )

        # Sort by compatibility score descending and return Top 5
        recommendations.sort(key=lambda r: r["predicted_score"], reverse=True)
        return recommendations[:5]
    except Exception as e:
        traceback.print_exc()
        logger.exception(f"Unhandled exception in recommendations router. Type: {type(e)}, details: {e}")
        raise e
