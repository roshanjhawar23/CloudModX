from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import utc_now


class Deployment(Base):
    """Deployment execution record for module versions."""
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(Integer, ForeignKey("module_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    environment = Column(String(50), nullable=False, default="dev")
    status = Column(String(50), nullable=False, default="queued", index=True)  # queued, running, success, failed, rolled_back
    deployed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    module = relationship("Module", back_populates="deployments")
    version = relationship("ModuleVersion", back_populates="deployments")
    deployer = relationship("User", back_populates="deployments")
