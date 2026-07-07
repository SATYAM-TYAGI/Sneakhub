"""Script to verify database connection and metadata tables."""

import sys
from sqlalchemy import text
from app.database import SessionLocal
from app.models import Base
from app.core.logging import get_logger

logger = get_logger("test_db_conn")


def test_connection():
    """Verify database connectivity and query execution."""
    logger.info("Attempting to connect to the database...")
    try:
        # Establish a session
        db = SessionLocal()
        # Execute basic query
        result = db.execute(text("SELECT 1")).fetchone()
        logger.info(
            f"Database connection successful! SELECT 1 returned: {result[0]}"
        )
        db.close()

        # Check tables in metadata
        logger.info("Registered tables in metadata:")
        for table_name in Base.metadata.tables.keys():
            logger.info(f" - {table_name}")

        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
