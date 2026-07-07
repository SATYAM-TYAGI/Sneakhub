"""Feature engineering and target compatibility score calculation helper module."""

import math
from typing import Dict, Any


def extract_pairwise_features(s1: Any, s2: Any) -> Dict[str, float]:
    """Generates a comparison feature vector between two sneaker records.

    Used by the ML training pipeline and the inference engine.
    """
    brand_match = 1.0 if s1.brand_id == s2.brand_id else 0.0
    category_match = 1.0 if s1.category_id == s2.category_id else 0.0

    # Case-insensitive matches for text attributes
    gender_match = (
        1.0 if str(s1.gender).lower() == str(s2.gender).lower() else 0.0
    )
    color_match = 1.0 if str(s1.color).lower() == str(s2.color).lower() else 0.0
    material_match = (
        1.0 if str(s1.material).lower() == str(s2.material).lower() else 0.0
    )

    # Absolute price difference
    price1 = float(s1.price_usd) if s1.price_usd is not None else 0.0
    price2 = float(s2.price_usd) if s2.price_usd is not None else 0.0
    abs_price_diff = abs(price1 - price2)

    return {
        "brand_match": brand_match,
        "category_match": category_match,
        "gender_match": gender_match,
        "color_match": color_match,
        "material_match": material_match,
        "abs_price_diff": abs_price_diff,
    }


def calculate_compatibility_score(s1: Any, s2: Any) -> float:
    """Calculates a weighted target compatibility score between two sneakers.

    Result is naturally scaled to [0, 100].
    Weights: Brand (30), Category (25), Color (15), Material (10), Gender (10), Price (10)
    """
    feats = extract_pairwise_features(s1, s2)

    # Weighted scores
    brand_score = feats["brand_match"] * 30.0
    category_score = feats["category_match"] * 25.0
    color_score = feats["color_match"] * 15.0
    material_score = feats["material_match"] * 10.0
    gender_score = feats["gender_match"] * 10.0

    # Exponential decay price similarity (maximum value of 10)
    # decay scale = 50.0 USD
    price_score = 10.0 * math.exp(-feats["abs_price_diff"] / 50.0)

    total_score = (
        brand_score
        + category_score
        + color_score
        + material_score
        + gender_score
        + price_score
    )

    # Clip to [0, 100] for safety
    return max(0.0, min(100.0, total_score))
