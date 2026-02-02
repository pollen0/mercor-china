import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

logger = logging.getLogger("pathway.database")

engine = create_engine(settings.database_url) if settings.database_url else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None

Base = declarative_base()


def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database not configured - DATABASE_URL environment variable is required")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(use_alembic: bool = True):
    """
    Initialize database tables.

    Args:
        use_alembic: If True (default), skip auto-creation and rely on Alembic migrations.
                    If False, use SQLAlchemy's create_all for development.

    For production, always use Alembic migrations:
        alembic upgrade head

    For quick development setup, you can call init_db(use_alembic=False).
    """
    if engine is None:
        logger.error("Database not configured - DATABASE_URL environment variable is required")
        raise RuntimeError("DATABASE_URL environment variable is required")

    # Import all models to ensure they are registered with Base
    from . import models  # noqa: F401

    if use_alembic:
        logger.info("Database initialization: Using Alembic migrations")
        logger.info("Run 'alembic upgrade head' to apply pending migrations")
    else:
        # Development mode: auto-create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully (dev mode)")


def check_db_connection() -> bool:
    """Check if database is accessible."""
    if engine is None:
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.warning(f"Database connection check failed: {e}")
        return False
