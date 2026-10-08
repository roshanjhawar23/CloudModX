from fastapi import APIRouter
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.modules import router as modules_router
from app.api.v1.endpoints.deployments import router as deployments_router
from app.api.v1.endpoints.audit_logs import router as audit_logs_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(modules_router, prefix="/modules", tags=["Modules"])
api_router.include_router(deployments_router, prefix="/deployments", tags=["Deployments"])
api_router.include_router(audit_logs_router, prefix="/audit-logs", tags=["Audit Logs"])
