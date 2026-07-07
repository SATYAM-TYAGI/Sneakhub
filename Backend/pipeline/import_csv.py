"""Pipeline script to clean and import the original Kaggle CSV into the database."""

import os
import sys
import time
from decimal import Decimal
import pandas as pd
from tqdm import tqdm
from sqlalchemy.orm import Session

# Add root Backend folder to sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.brand import Brand
from app.models.category import Category
from app.models.sneaker import Sneaker
from app.core.logging import get_logger

logger = get_logger("import_csv")


def run_import(csv_path: str = "Data/Shoes.csv"):
    """Loads, cleans, deduplicates, and loads the original sneaker CSV into the database.

    Runs within a single transaction and rolls back on failure.
    """
    start_time = time.time()
    logger.info(f"Starting CSV import from path: {csv_path}")

    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found at: {csv_path}")
        return

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        logger.error(f"Failed to read CSV file: {e}")
        return

    rows_read = len(df)
    logger.info(f"Loaded CSV successfully. Rows read: {rows_read}")

    # Validate required columns
    required_cols = [
        "Brand",
        "Model",
        "Type",
        "Gender",
        "Color",
        "Material",
        "Price (USD)",
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.error(f"Missing required columns in CSV: {missing_cols}")
        return

    # Normalize: strip whitespace from all string object columns
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()

    # Drop duplicate rows based on dedup columns, keeping the first occurrence
    dedup_cols = ["Brand", "Model", "Type", "Gender", "Color", "Material"]
    df = df.drop_duplicates(subset=dedup_cols, keep="first")
    cleaned_rows_count = len(df)
    duplicates_in_csv = rows_read - cleaned_rows_count
    logger.info(
        f"Cleaned duplicate rows in CSV. Unique rows count: {cleaned_rows_count} "
        f"(Skipped {duplicates_in_csv} duplicates within the CSV source)"
    )

    db: Session = SessionLocal()

    rows_imported = 0
    duplicates_skipped = 0
    errors_count = 0

    try:
        # Load existing brands/categories/sneakers for in-memory mapping
        brands_cache = {b.name.lower(): b.id for b in db.query(Brand).all()}
        categories_cache = {
            c.name.lower(): c.id for c in db.query(Category).all()
        }
        existing_sneakers = {
            (
                s.brand_id,
                s.model_name.lower(),
                s.category_id,
                s.gender,
                s.color.lower(),
                s.material.lower(),
            )
            for s in db.query(Sneaker).all()
        }

        # Iterate over dataframe rows with progress logging
        for _, row in tqdm(
            df.iterrows(), total=cleaned_rows_count, desc="Importing Sneakers"
        ):
            try:
                brand_name = str(row["Brand"])
                model_name = str(row["Model"])
                category_name = str(row["Type"])
                gender_str = str(row["Gender"])
                color_str = str(row["Color"])
                material_str = str(row["Material"])
                price_str = str(row["Price (USD)"])

                # Normalize Gender: lowercase, map men/women or default to unisex
                gender_lower = gender_str.lower()
                if gender_lower in ["men", "women", "unisex"]:
                    gender_norm = gender_lower
                else:
                    gender_norm = "unisex"

                # Normalize Price: parse string like "$170.00"
                clean_price_str = (
                    price_str.replace("$", "").replace(",", "").strip()
                )
                try:
                    price_val = Decimal(clean_price_str)
                    if price_val < 0:
                        raise ValueError("Price cannot be negative")
                except Exception as val_err:
                    logger.warning(
                        f"Invalid price value '{price_str}' for sneaker {brand_name} {model_name}: {val_err}"
                    )
                    errors_count += 1
                    continue

                # Get or Create Brand slug
                brand_key = brand_name.lower()
                if brand_key not in brands_cache:
                    brand_slug = (
                        brand_key.replace(" ", "-")
                        .replace("/", "-")
                        .replace("\\", "-")
                    )
                    new_brand = Brand(name=brand_name, slug=brand_slug)
                    db.add(new_brand)
                    db.flush()  # generate ID
                    brands_cache[brand_key] = new_brand.id
                brand_id = brands_cache[brand_key]

                # Get or Create Category slug
                category_key = category_name.lower()
                if category_key not in categories_cache:
                    category_slug = (
                        category_key.replace(" ", "-")
                        .replace("/", "-")
                        .replace("\\", "-")
                    )
                    new_cat = Category(name=category_name, slug=category_slug)
                    db.add(new_cat)
                    db.flush()  # generate ID
                    categories_cache[category_key] = new_cat.id
                category_id = categories_cache[category_key]

                # Skip duplicate sneakers
                sneaker_key = (
                    brand_id,
                    model_name.lower(),
                    category_id,
                    gender_norm,
                    color_str.lower(),
                    material_str.lower(),
                )

                if sneaker_key in existing_sneakers:
                    duplicates_skipped += 1
                    continue

                # Create and insert sneaker ORM entity
                display_name = f"{brand_name} {model_name}"
                new_sneaker = Sneaker(
                    brand_id=brand_id,
                    category_id=category_id,
                    model_name=model_name,
                    display_name=display_name,
                    gender=gender_norm,
                    color=color_str,
                    material=material_str,
                    price_usd=price_val,
                    is_active=True,
                )
                db.add(new_sneaker)
                db.flush()

                # Register key to avoid duplicates inside loop
                existing_sneakers.add(sneaker_key)
                rows_imported += 1

            except Exception as row_err:
                logger.error(
                    f"Error processing row '{row.to_dict()}': {row_err}"
                )
                errors_count += 1

        db.commit()
        logger.info("Successfully committed transaction.")
    except Exception as e:
        db.rollback()
        logger.critical(f"Transaction failed and was rolled back: {e}")
        errors_count += 1
    finally:
        db.close()

    elapsed = time.time() - start_time
    logger.info("========================================")
    logger.info("ETL IMPORT SUMMARY")
    logger.info(f"Rows Read:          {rows_read}")
    logger.info(f"Rows Imported:      {rows_imported}")
    logger.info(f"Duplicates Skipped: {duplicates_skipped}")
    logger.info(f"Errors:             {errors_count}")
    logger.info(f"Elapsed Time:       {elapsed:.2f} seconds")
    logger.info("========================================")


if __name__ == "__main__":
    # If run directly as a script
    csv_file = "Data/Shoes.csv"
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    run_import(csv_file)
