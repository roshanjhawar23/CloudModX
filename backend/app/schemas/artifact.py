from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ArtifactBase(BaseModel):
    filename: str
    storage_provider: str = "s3"
    storage_path: str
    size_bytes: int = 0
    checksum: Optional[str] = None


class ArtifactCreate(ArtifactBase):
    module_id: int
    version: str


class ArtifactRead(ArtifactBase):
    id: int
    module_id: int
    version: str
    created_at: datetime

    class Config:
        from_attributes = True
