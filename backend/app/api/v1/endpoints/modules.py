import json
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.artifact import Artifact
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.module import ModuleRead, ModuleDetail, ModuleCreate, ModuleStatusUpdate
from app.schemas.module_version import ModuleVersionRead, ModuleVersionCreate
from app.schemas.artifact import ArtifactRead
from app.schemas.deployment import DeploymentRead
from app.services.s3_service import s3_service

router = APIRouter()


@router.get("", response_model=List[ModuleRead])
def list_modules(
    status: Optional[str] = None,
    environment: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all registered CloudModX modules with optional status/environment filters."""
    query = db.query(Module)
    if status:
        query = query.filter(Module.status == status.lower())
    if environment:
        query = query.filter(Module.environment == environment.lower())
    return query.order_by(Module.id.asc()).all()


@router.post("", response_model=ModuleRead, status_code=status.HTTP_201_CREATED)
def create_module(
    module_in: ModuleCreate,
    db: Session = Depends(get_db),
):
    """Register a new CloudModX cloud-native module."""
    # Ensure default owner exists if owner_id provided
    owner = db.query(User).filter(User.id == module_in.owner_id).first()
    if not owner:
        # Fallback to first user in database or create default
        owner = db.query(User).first()
        if not owner:
            owner = User(name="Admin User", email="admin@cloudmodx.local", role="admin")
            db.add(owner)
            db.flush()

    new_module = Module(
        name=module_in.name,
        description=module_in.description,
        owner_id=owner.id,
        technology=module_in.technology,
        architecture=module_in.architecture,
        environment=module_in.environment,
        status=module_in.status or "draft",
        repository_url=module_in.repository_url,
    )
    db.add(new_module)
    db.flush()

    # Create audit log entry
    audit = AuditLog(
        user_id=owner.id,
        action="CREATE_MODULE",
        resource_type="module",
        resource_id=str(new_module.id),
        details=json.dumps({"name": new_module.name, "status": new_module.status}),
    )
    db.add(audit)
    db.commit()
    db.refresh(new_module)
    return new_module


@router.get("/{module_id}", response_model=ModuleDetail)
def get_module(module_id: int, db: Session = Depends(get_db)):
    """Retrieve full details of a module including versions, artifacts, and deployments."""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module


@router.patch("/{module_id}/status", response_model=ModuleRead)
def update_module_status(
    module_id: int,
    status_in: ModuleStatusUpdate,
    db: Session = Depends(get_db),
):
    """Transition module lifecycle stage (draft -> review -> approved -> active -> archived)."""
    valid_statuses = {"draft", "review", "approved", "active", "archived"}
    new_status = status_in.status.lower()
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{new_status}'. Allowed: {', '.join(valid_statuses)}",
        )

    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    old_status = module.status
    module.status = new_status

    audit = AuditLog(
        user_id=module.owner_id,
        action="UPDATE_MODULE_STATUS",
        resource_type="module",
        resource_id=str(module.id),
        details=json.dumps({"from": old_status, "to": new_status}),
    )
    db.add(audit)
    db.commit()
    db.refresh(module)
    return module


@router.post("/{module_id}/versions", response_model=ModuleVersionRead, status_code=status.HTTP_201_CREATED)
def create_module_version(
    module_id: int,
    version_in: ModuleVersionCreate,
    db: Session = Depends(get_db),
):
    """Create a new version release for a module."""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    existing = db.query(ModuleVersion).filter(
        ModuleVersion.module_id == module_id,
        ModuleVersion.version == version_in.version,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Version {version_in.version} already exists for this module")

    new_version = ModuleVersion(
        module_id=module_id,
        version=version_in.version,
        release_notes=version_in.release_notes,
    )
    db.add(new_version)
    db.flush()

    audit = AuditLog(
        user_id=module.owner_id,
        action="CREATE_VERSION",
        resource_type="module_version",
        resource_id=str(new_version.id),
        details=json.dumps({"module_id": module_id, "version": new_version.version}),
    )
    db.add(audit)
    db.commit()
    db.refresh(new_version)
    return new_version


@router.post("/{module_id}/versions/{version_id}/artifact", response_model=ArtifactRead, status_code=status.HTTP_201_CREATED)
async def upload_version_artifact(
    module_id: int,
    version_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a build/package artifact to S3 and link it to the module version."""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    version = db.query(ModuleVersion).filter(
        ModuleVersion.id == version_id,
        ModuleVersion.module_id == module_id,
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="Module version not found")

    content = await file.read()
    provider, storage_path, size_bytes, checksum = s3_service.upload_artifact(
        file_content=content,
        filename=file.filename,
        module_id=module_id,
        version=version.version,
    )

    artifact = Artifact(
        module_id=module_id,
        version=version.version,
        filename=file.filename,
        storage_provider=provider,
        storage_path=storage_path,
        size_bytes=size_bytes,
        checksum=checksum,
    )
    db.add(artifact)
    db.flush()

    # Link artifact to the version
    version.artifact_id = artifact.id

    audit = AuditLog(
        user_id=module.owner_id,
        action="UPLOAD_ARTIFACT",
        resource_type="artifact",
        resource_id=str(artifact.id),
        details=json.dumps({
            "module_id": module_id,
            "version": version.version,
            "filename": artifact.filename,
            "storage_path": artifact.storage_path,
            "size_bytes": artifact.size_bytes,
        }),
    )
    db.add(audit)
    db.commit()
    db.refresh(artifact)
    return artifact


@router.post("/{module_id}/rollback", response_model=DeploymentRead, status_code=status.HTTP_201_CREATED)
def rollback_module(
    module_id: int,
    environment: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Direct module rollback trigger to previous stable version."""
    from app.api.v1.endpoints.deployments import rollback_deployment
    from app.schemas.deployment import RollbackRequest
    return rollback_deployment(RollbackRequest(module_id=module_id, environment=environment), db)
