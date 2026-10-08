from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogRead

router = APIRouter()


@router.get("", response_model=List[AuditLogRead])
def list_audit_logs(
    resource_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List system and user audit log records in reverse chronological order."""
    query = db.query(AuditLog)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
