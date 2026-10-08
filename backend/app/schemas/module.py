from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserRead
from app.schemas.module_version import ModuleVersionRead
from app.schemas.deployment import DeploymentRead


class ModuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    technology: str = "Python / FastAPI"
    architecture: str = "Microservice"
    environment: str = "development"
    status: str = "draft"
    repository_url: Optional[str] = None


class ModuleCreate(ModuleBase):
    owner_id: Optional[int] = 1


class ModuleStatusUpdate(BaseModel):
    status: str  # draft, review, approved, active, archived


class ModuleRead(ModuleBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    owner: Optional[UserRead] = None

    class Config:
        from_attributes = True


class ModuleDetail(ModuleRead):
    versions: List[ModuleVersionRead] = []
    deployments: List[DeploymentRead] = []
