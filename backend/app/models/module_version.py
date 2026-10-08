from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import utc_now


class ModuleVersion(Base):
    """Specific version release of a CloudModX module."""
    __tablename__ = "module_versions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(String(50), nullable=False, index=True)
    release_notes = Column(Text, nullable=True)
    artifact_id = Column(Integer, ForeignKey("artifacts.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    module = relationship("Module", back_populates="versions")
    artifact = relationship("Artifact", back_populates="versions")
    deployments = relationship("Deployment", back_populates="version", cascade="all, delete-orphan")
