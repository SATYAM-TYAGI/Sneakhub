"""Script to seed initial database reference data (brands and categories)."""

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.brand import Brand
from app.models.category import Category
from app.core.logging import get_logger

logger = get_logger("seed_database")

DEFAULT_BRANDS = [
    {"name": "Nike", "slug": "nike"},
    {"name": "Adidas", "slug": "adidas"},
    {"name": "New Balance", "slug": "new-balance"},
    {"name": "Reebok", "slug": "reebok"},
    {"name": "Puma", "slug": "puma"},
    {"name": "Vans", "slug": "vans"},
    {"name": "Converse", "slug": "converse"},
    {"name": "Asics", "slug": "asics"},
    {"name": "Skechers", "slug": "skechers"},
    {"name": "Fila", "slug": "fila"},
]

DEFAULT_CATEGORIES = [
    {"name": "Running", "slug": "running"},
    {"name": "Casual", "slug": "casual"},
    {"name": "Basketball", "slug": "basketball"},
    {"name": "Skate", "slug": "skate"},
    {"name": "Training", "slug": "training"},
    {"name": "Walking", "slug": "walking"},
]


def seed(db: Session):
    """Seed brands and categories, checking for existing entries."""
    logger.info("Starting database seeding...")

    # Seed Brands
    for brand_data in DEFAULT_BRANDS:
        existing = (
            db.query(Brand).filter(Brand.slug == brand_data["slug"]).first()
        )
        if not existing:
            brand = Brand(name=brand_data["name"], slug=brand_data["slug"])
            db.add(brand)
            logger.info(f"Seeding brand: {brand_data['name']}")
        else:
            logger.info(f"Brand {brand_data['name']} already exists, skipping.")

    # Seed Categories
    for cat_data in DEFAULT_CATEGORIES:
        existing = (
            db.query(Category)
            .filter(Category.slug == cat_data["slug"])
            .first()
        )
        if not existing:
            category = Category(name=cat_data["name"], slug=cat_data["slug"])
            db.add(category)
            logger.info(f"Seeding category: {cat_data['name']}")
        else:
            logger.info(
                f"Category {cat_data['name']} already exists, skipping."
            )

    try:
        db.commit()
        logger.info("Database seeding completed successfully!")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during seeding: {e}")
        raise e


if __name__ == "__main__":
    db_session = SessionLocal()
    try:
        seed(db_session)
    finally:
        db_session.close()
