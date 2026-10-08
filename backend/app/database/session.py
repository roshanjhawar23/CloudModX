import logging
from typing import Generator, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base for models
Base = declarative_base()

# SQLAlchemy Engine & Session
engine = None
SessionLocal = None


def init_engine():
    """Initialize SQLAlchemy engine and sessionmaker using the psycopg2 driver URL."""
    global engine, SessionLocal
    db_url = settings.sync_database_url or settings.DATABASE_URL
    if db_url:
        try:
            engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=settings.ENVIRONMENT == "development",
            )
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            logger.info("SQLAlchemy database engine initialized successfully with psycopg2 driver.")
        except Exception as e:
            logger.warning(f"Database engine initialization failed: {e}")
    return engine


# Initial engine setup
init_engine()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency to yield a database session per request."""
    global engine, SessionLocal
    if SessionLocal is None:
        init_engine()
    if SessionLocal is None:
        raise RuntimeError("Database session factory is not configured.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_health() -> Tuple[bool, str]:
    """Execute lightweight query (SELECT 1) to verify live database connectivity."""
    global engine
    if engine is None:
        init_engine()
    if engine is None:
        return False, "Database engine is not configured."
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            if result == 1:
                return True, "Database connection healthy."
            return False, f"Unexpected response from database: {result}"
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return False, f"Database unavailable: {str(e)}"
