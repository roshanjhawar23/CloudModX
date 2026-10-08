from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime
from app.database.session import Base


def utc_now():
    """Helper to return current UTC datetime."""
    return datetime.now(timezone.utc)


class BaseModel(Base):
    """Abstract base model with primary key and timestamp tracking."""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
