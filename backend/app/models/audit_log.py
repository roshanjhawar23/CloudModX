from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.base import utc_now


class AuditLog(Base):
    """Audit log tracking system and user mutations."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # e.g., CREATE_MODULE, DEPLOY, UPDATE_STATUS
    resource_type = Column(String(100), nullable=False, index=True)  # e.g., module, deployment, user
    resource_id = Column(String(100), nullable=True, index=True)
    details = Column(Text, nullable=True)  # JSON or text description
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
