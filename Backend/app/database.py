from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

logger.info(
    "Initializing database connection pool with pool_size=3 and max_overflow=2"
)

# SQLAlchemy engine with centralized configurations and pooling limit parameters
engine = create_engine(
    settings.database_url,
    pool_size=3,
    max_overflow=2,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency generator to yield database sessions.

    Automatically closes the session after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
