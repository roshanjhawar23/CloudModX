from pydantic import BaseModel
from typing import Optional


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    database_connected: bool
    database_configured: bool
    database_status: str
    details: Optional[str] = None
