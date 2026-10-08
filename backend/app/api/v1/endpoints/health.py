from fastapi import APIRouter
from app.core.config import settings
from app.schemas.health import HealthResponse
from app.database.session import check_db_health

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Service & Database Health Check")
def get_health() -> HealthResponse:
    """Return health status by executing a real lightweight query (SELECT 1) against the database."""
    db_connected, db_msg = check_db_health()
    overall_status = "healthy" if db_connected else "degraded"
    
    details = (
        "CloudModX platform application and PostgreSQL database are healthy."
        if db_connected
        else f"CloudModX application running; database unavailable ({db_msg})."
    )

    return HealthResponse(
        status=overall_status,
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database_connected=db_connected,
        database_configured=bool(settings.sync_database_url or settings.DATABASE_URL),
        database_status="connected" if db_connected else "disconnected",
        details=details,
    )
