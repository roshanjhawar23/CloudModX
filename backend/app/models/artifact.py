from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import utc_now


class Artifact(Base):
    """Artifact metadata associated with build and package storage."""
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    filename = Column(String(255), nullable=False)
    storage_provider = Column(String(50), nullable=False, default="local")  # local, s3
    storage_path = Column(String(500), nullable=False)
    size_bytes = Column(BigInteger, nullable=False, default=0)
    checksum = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    module = relationship("Module", back_populates="artifacts")
    versions = relationship("ModuleVersion", back_populates="artifact")
