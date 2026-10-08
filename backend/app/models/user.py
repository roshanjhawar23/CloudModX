from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    """User entity for authentication and ownership tracking."""
    __tablename__ = "users"

    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(50), nullable=False, default="developer")  # admin, developer, viewer

    # Relationships
    modules = relationship("Module", back_populates="owner", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="deployer")
    audit_logs = relationship("AuditLog", back_populates="user")
