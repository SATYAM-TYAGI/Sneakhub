def build_query(
    brand: str,
    model: str,
    color: str,
    gender: str,
    category: str,
    material: str,
) -> str:
    """Builds a descriptive, multi-attribute search query string for sneaker lookup.

    Example:
        ("Nike", "Air Max 90", "White", "men", "Running", "Mesh")
        -> "Nike Air Max 90 White Men's Running Mesh"
    """
    gender_map = {
        "men": "Men's",
        "women": "Women's",
        "unisex": "Unisex",
    }
    gender_display = gender_map.get(gender.lower(), "Unisex")

    parts = [brand, model, color, gender_display, category, material]
    # Remove any empty or whitespace-only elements
    clean_parts = [str(p).strip() for p in parts if p and str(p).strip()]

    return " ".join(clean_parts)
