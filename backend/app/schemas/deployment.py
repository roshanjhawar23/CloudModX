from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeploymentBase(BaseModel):
    environment: str = "dev"
    status: str = "queued"
    error_message: Optional[str] = None


class DeploymentCreate(BaseModel):
    module_id: int
    version_id: int
    environment: str = "production"
    deployed_by: Optional[int] = None
    simulate_failure: Optional[bool] = False


class RollbackRequest(BaseModel):
    module_id: int
    environment: Optional[str] = "production"
    deployed_by: Optional[int] = None


class DeploymentRead(DeploymentBase):
    id: int
    module_id: int
    version_id: int
    deployed_by: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
