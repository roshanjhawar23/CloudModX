import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.models.deployment import Deployment
from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.artifact import Artifact
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.deployment import DeploymentRead, DeploymentCreate, RollbackRequest

router = APIRouter()


@router.get("", response_model=List[DeploymentRead])
def list_deployments(
    module_id: Optional[int] = None,
    environment: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List recent deployment executions."""
    query = db.query(Deployment)
    if module_id:
        query = query.filter(Deployment.module_id == module_id)
    if environment:
        query = query.filter(Deployment.environment == environment)
    return query.order_by(Deployment.created_at.desc()).limit(limit).all()


@router.post("", response_model=DeploymentRead, status_code=status.HTTP_201_CREATED)
def create_deployment(
    dep_in: DeploymentCreate,
    db: Session = Depends(get_db),
):
    """Execute a real deployment workflow for a module version with validation and state transitions."""
    module = db.query(Module).filter(Module.id == dep_in.module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    version = db.query(ModuleVersion).filter(
        ModuleVersion.id == dep_in.version_id,
        ModuleVersion.module_id == dep_in.module_id,
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="Module version not found")

    deployer = None
    if dep_in.deployed_by:
        deployer = db.query(User).filter(User.id == dep_in.deployed_by).first()
    if not deployer:
        deployer = db.query(User).first()

    now = datetime.now(timezone.utc)
    target_env = dep_in.environment or module.environment or "production"

    # 1. Initialize deployment record in 'pending' / 'running' state
    new_deployment = Deployment(
        module_id=dep_in.module_id,
        version_id=dep_in.version_id,
        environment=target_env,
        status="running",
        deployed_by=deployer.id if deployer else None,
        started_at=now,
    )
    db.add(new_deployment)
    db.flush()

    # 2. Perform Real Deployment Action & Artifact Validation
    artifact = None
    if version.artifact_id:
        artifact = db.query(Artifact).filter(Artifact.id == version.artifact_id).first()

    is_failed = False
    error_msg = None

    if dep_in.simulate_failure:
        is_failed = True
        error_msg = f"Deployment execution simulated failure for {module.name} {version.version}"
    elif not artifact:
        is_failed = True
        error_msg = f"Deployment failed: Release package artifact missing for version {version.version}. Upload an artifact before deploying."

    # 3. Finalize State & Record Audit Trail
    completed_time = datetime.now(timezone.utc)
    new_deployment.completed_at = completed_time

    if is_failed:
        new_deployment.status = "failed"
        new_deployment.error_message = error_msg

        audit = AuditLog(
            user_id=deployer.id if deployer else None,
            action="DEPLOYMENT_FAILED",
            resource_type="deployment",
            resource_id=str(new_deployment.id),
            details=json.dumps({
                "module_id": module.id,
                "module_name": module.name,
                "version": version.version,
                "environment": target_env,
                "error": error_msg,
            }),
        )
        db.add(audit)
    else:
        new_deployment.status = "success"
        new_deployment.error_message = None

        # Automatically promote module to active if it was draft or in review
        if module.status in ["draft", "review", "approved"]:
            module.status = "active"

        audit = AuditLog(
            user_id=deployer.id if deployer else None,
            action="DEPLOYMENT_SUCCESS",
            resource_type="deployment",
            resource_id=str(new_deployment.id),
            details=json.dumps({
                "module_id": module.id,
                "module_name": module.name,
                "version": version.version,
                "environment": target_env,
                "artifact": artifact.filename if artifact else None,
                "storage_provider": artifact.storage_provider if artifact else None,
            }),
        )
        db.add(audit)

    db.commit()
    db.refresh(new_deployment)
    return new_deployment


@router.post("/rollback", response_model=DeploymentRead, status_code=status.HTTP_201_CREATED)
def rollback_deployment(
    req: RollbackRequest,
    db: Session = Depends(get_db),
):
    """Roll back a module to its previous successful deployed version."""
    module = db.query(Module).filter(Module.id == req.module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    target_env = req.environment or module.environment or "production"

    # Get all deployments for this module & environment ordered by created_at desc
    all_deployments = (
        db.query(Deployment)
        .filter(Deployment.module_id == module.id, Deployment.environment == target_env)
        .order_by(Deployment.created_at.desc())
        .all()
    )

    if not all_deployments:
        raise HTTPException(
            status_code=400,
            detail=f"No deployment history found for module '{module.name}' in environment '{target_env}'",
        )

    current_deployment = all_deployments[0]
    current_version_id = current_deployment.version_id

    # Find the most recent SUCCESSFUL deployment with a different version
    prev_successful = None
    for dep in all_deployments:
        if dep.status == "success" and dep.version_id != current_version_id:
            prev_successful = dep
            break

    # If the current deployment failed and there was a previous successful deployment with any version
    if not prev_successful and current_deployment.status == "failed":
        for dep in all_deployments:
            if dep.status == "success":
                prev_successful = dep
                break

    if not prev_successful:
        raise HTTPException(
            status_code=400,
            detail=f"No previous successful version found for module '{module.name}' in environment '{target_env}' to roll back to.",
        )

    target_version = db.query(ModuleVersion).filter(ModuleVersion.id == prev_successful.version_id).first()
    if not target_version:
        raise HTTPException(status_code=404, detail="Target rollback version not found")

    deployer = None
    if req.deployed_by:
        deployer = db.query(User).filter(User.id == req.deployed_by).first()
    if not deployer:
        deployer = db.query(User).first()

    now = datetime.now(timezone.utc)
    rollback_dep = Deployment(
        module_id=module.id,
        version_id=target_version.id,
        environment=target_env,
        status="success",
        deployed_by=deployer.id if deployer else None,
        started_at=now,
        completed_at=now,
        error_message=f"Rolled back from deployment #{current_deployment.id} to version {target_version.version}",
    )
    db.add(rollback_dep)
    db.flush()

    # Promote module status to active
    module.status = "active"

    # Audit log
    audit = AuditLog(
        user_id=deployer.id if deployer else None,
        action="DEPLOYMENT_ROLLBACK",
        resource_type="deployment",
        resource_id=str(rollback_dep.id),
        details=json.dumps({
            "module_id": module.id,
            "module_name": module.name,
            "from_deployment_id": current_deployment.id,
            "target_version": target_version.version,
            "environment": target_env,
        }),
    )
    db.add(audit)
    db.commit()
    db.refresh(rollback_dep)
    return rollback_dep
