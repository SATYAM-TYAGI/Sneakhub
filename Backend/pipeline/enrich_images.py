"""Pipeline script to enrich sneakers with image and product URLs from search providers."""

import os
import sys
import tempfile
from typing import Optional
import httpx
from sqlalchemy.orm import Session
from tqdm import tqdm
import cloudinary
import cloudinary.uploader

# Add root Backend folder to sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.sneaker import Sneaker
from app.config import settings
from app.core.logging import get_logger
from pipeline.search import (
    BaseSearchProvider,
    DuckDuckGoProvider,
    SerpAPIProvider,
    StockXProvider,
    ManualProvider,
    build_query,
)

logger = get_logger("enrich_images")

# Configure Cloudinary credentials if present in settings
CLOUDINARY_CLOUD_NAME = getattr(settings, "cloudinary_cloud_name", None)
CLOUDINARY_API_KEY = getattr(settings, "cloudinary_api_key", None)
CLOUDINARY_API_SECRET = getattr(settings, "cloudinary_api_secret", None)

if all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )
    CLOUDINARY_CONFIGURED = True
    logger.info("Cloudinary is successfully configured.")
else:
    logger.warning(
        "Cloudinary credentials are not configured in settings. "
        "Script will save direct search image URLs instead of uploading."
    )
    CLOUDINARY_CONFIGURED = False


def get_search_provider() -> BaseSearchProvider:
    """Instantiate the search provider configured in settings."""
    provider_name = str(settings.search_provider).lower().strip()
    if provider_name == "serpapi":
        return SerpAPIProvider()
    elif provider_name == "stockx":
        return StockXProvider()
    elif provider_name == "manual":
        return ManualProvider()
    else:
        return DuckDuckGoProvider()


def download_image(url: str) -> Optional[str]:
    """Download an image from a URL into a temporary file.

    Returns the path to the temp file on success, or None on failure.
    """
    from typing import Optional

    try:
        response = httpx.get(url, timeout=10.0, follow_redirects=True)
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                logger.warning(
                    f"Downloaded content from {url} is not an image "
                    f"(Content-Type: {content_type})"
                )
                return None

            # Determine suffix extension
            suffix = ".jpg"
            if "png" in content_type:
                suffix = ".png"
            elif "webp" in content_type:
                suffix = ".webp"

            # Create temporary file
            fd, temp_path = tempfile.mkstemp(suffix=suffix)
            with os.fdopen(fd, "wb") as tmp:
                tmp.write(response.content)
            return temp_path
    except Exception as e:
        logger.error(f"Failed to download image from {url}: {e}")
    return None


def upload_to_cloudinary(file_path: str, public_id: str) -> Optional[str]:
    """Upload a local image file to Cloudinary.

    Returns the secure URL on success, or None on failure.
    """
    from typing import Optional

    try:
        result = cloudinary.uploader.upload(
            file_path, public_id=public_id, folder="sneakers", overwrite=True
        )
        return result.get("secure_url")
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
    return None


def enrich_images(limit: Optional[int] = None):
    """Scan database for sneakers missing images, query search provider, and save results."""
    from typing import Optional

    db: Session = SessionLocal()
    provider = get_search_provider()

    # Find sneakers where image_url is missing or empty
    query = db.query(Sneaker).filter(
        (Sneaker.image_url.is_(None)) | (Sneaker.image_url == "")
    )
    if limit:
        query = query.limit(limit)

    sneakers = query.all()
    if not sneakers:
        logger.info("All sneakers already have image URLs. No enrichment needed.")
        db.close()
        return

    logger.info(
        f"Found {len(sneakers)} sneakers without images. Starting enrichment..."
    )

    success_count = 0
    fail_count = 0

    for sneaker in tqdm(sneakers, desc="Enriching Images"):
        try:
            # Generate the query using the sneaker details relationships
            query_str = build_query(
                brand=sneaker.brand.name,
                model=sneaker.model_name,
                color=sneaker.color,
                gender=sneaker.gender,
                category=sneaker.category.name,
                material=sneaker.material,
            )

            # Search
            search_res = provider.search(query_str)
            if not search_res.image_url:
                logger.warning(
                    f"Search provider returned no image URL for: '{query_str}'"
                )
                fail_count += 1
                continue

            product_url = search_res.product_url
            searched_url = search_res.image_url

            final_image_url = None

            if CLOUDINARY_CONFIGURED:
                # Download and upload to Cloudinary
                temp_file = download_image(searched_url)
                if temp_file:
                    try:
                        clean_name = (
                            sneaker.display_name.lower()
                            .replace(" ", "-")
                            .replace("/", "-")
                        )
                        public_id = f"{sneaker.id}-{clean_name}"
                        cloudinary_url = upload_to_cloudinary(
                            temp_file, public_id
                        )
                        if cloudinary_url:
                            final_image_url = cloudinary_url
                            logger.info(
                                f"Uploaded image to Cloudinary: {final_image_url}"
                            )
                    finally:
                        # Ensure cleanup of temp file
                        try:
                            if os.path.exists(temp_file):
                                os.remove(temp_file)
                                logger.info(
                                    f"Deleted temporary file: {temp_file}"
                                )
                        except Exception as rm_err:
                            logger.error(
                                f"Failed to delete temporary file {temp_file}: {rm_err}"
                            )
                else:
                    logger.error(
                        f"Failed to download image from {searched_url} for sneaker ID: {sneaker.id}"
                    )
            else:
                # Fallback to direct search URL
                final_image_url = searched_url
                logger.info(
                    f"Saving direct search image URL (Cloudinary not configured): {final_image_url}"
                )

            if final_image_url:
                sneaker.image_url = final_image_url
                if product_url:
                    sneaker.product_url = product_url
                sneaker.search_query_used = query_str

                db.commit()
                success_count += 1
            else:
                fail_count += 1

        except Exception as sneaker_err:
            db.rollback()
            logger.error(
                f"Error processing sneaker ID {sneaker.id}: {sneaker_err}"
            )
            fail_count += 1

    db.close()
    logger.info(
        f"Enrichment completed. Success: {success_count}, Failed: {fail_count}"
    )


if __name__ == "__main__":
    # If run directly as a script, default limit to 10 for safety/demo
    limit_arg = 10
    if len(sys.argv) > 1:
        try:
            limit_arg = int(sys.argv[1])
        except ValueError:
            pass
    enrich_images(limit=limit_arg)
