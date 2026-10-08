from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Module(BaseModel):
    """CloudModX module entity representing college cloud-native services."""
    __tablename__ = "modules"

    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    technology = Column(String(100), nullable=False)
    architecture = Column(String(100), nullable=False)
    environment = Column(String(50), nullable=False, default="development")
    status = Column(String(50), nullable=False, default="draft", index=True)  # draft, review, approved, active, archived
    repository_url = Column(String(255), nullable=True)

    # Relationships
    owner = relationship("User", back_populates="modules")
    versions = relationship("ModuleVersion", back_populates="module", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="module", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="module", cascade="all, delete-orphan")
