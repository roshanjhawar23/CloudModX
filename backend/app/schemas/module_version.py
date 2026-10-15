from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.schemas.artifact import ArtifactRead


class ModuleVersionBase(BaseModel):
    version: str
    release_notes: Optional[str] = None


class ModuleVersionCreate(ModuleVersionBase):
    pass


class ModuleVersionRead(ModuleVersionBase):
    id: int
    module_id: int
    artifact_id: Optional[int] = None
    created_at: datetime
    artifact: Optional[ArtifactRead] = None

    model_config = ConfigDict(from_attributes=True)
