from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.user import UserRead


class AuditLogBase(BaseModel):
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    user_id: Optional[int] = None


class AuditLogRead(AuditLogBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    user: Optional[UserRead] = None

    class Config:
        from_attributes = True
