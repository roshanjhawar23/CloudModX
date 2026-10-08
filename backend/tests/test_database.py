import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models.module import Module
from app.models.artifact import Artifact
from app.models.module_version import ModuleVersion
from app.models.deployment import Deployment
from app.models.audit_log import AuditLog
from app.database.seed import seed_database


def test_database_connection(db_session):
    """Verify basic database connectivity and simple query execution."""
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_model_creation(db_session):
    """Verify user model creation and standard properties."""
    user = User(
        name="Jane Professor",
        email="jane.prof@college.edu",
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.name == "Jane Professor"
    assert user.email == "jane.prof@college.edu"
    assert user.role == "admin"
    assert user.created_at is not None
    assert user.updated_at is not None


def test_unique_user_email_constraint(db_session):
    """Verify unique constraint on user email."""
    user1 = User(name="User One", email="unique@college.edu", role="developer")
    db_session.add(user1)
    db_session.commit()

    user2 = User(name="User Two", email="unique@college.edu", role="viewer")
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_module_creation(db_session):
    """Verify module creation and association with user owner."""
    owner = User(name="Curriculum Lead", email="lead@college.edu", role="admin")
    db_session.add(owner)
    db_session.commit()

    module = Module(
        name="Microservices Architecture 101",
        description="Foundational cloud microservices course module.",
        owner_id=owner.id,
        technology="Python / FastAPI",
        architecture="Cloud-Native",
        environment="development",
        status="draft",
        repository_url="https://github.com/cloudmodx/ms-101",
    )
    db_session.add(module)
    db_session.commit()
    db_session.refresh(module)

    assert module.id is not None
    assert module.owner.name == "Curriculum Lead"
    assert module.status == "draft"


def test_version_relationship(db_session):
    """Verify module versions, artifacts, and bidirectional relationships."""
    owner = User(name="Prof. Turing", email="turing@college.edu", role="admin")
    db_session.add(owner)
    db_session.commit()

    module = Module(
        name="Data Structures in Cloud",
        description="Cloud distributed data structures.",
        owner_id=owner.id,
        technology="Go",
        architecture="Microservice",
        environment="development",
        status="approved",
    )
    db_session.add(module)
    db_session.commit()

    artifact = Artifact(
        module_id=module.id,
        version="1.0.0",
        filename="ds-cloud-v1.0.0.tar.gz",
        storage_provider="local",
        storage_path="/storage/ds-cloud-v1.0.0.tar.gz",
        size_bytes=5242880,
        checksum="sha256:abcd1234efgh5678",
    )
    db_session.add(artifact)
    db_session.commit()

    version = ModuleVersion(
        module_id=module.id,
        version="1.0.0",
        release_notes="First release candidate.",
        artifact_id=artifact.id,
    )
    db_session.add(version)
    db_session.commit()

    db_session.refresh(module)
    db_session.refresh(version)

    assert len(module.versions) == 1
    assert module.versions[0].version == "1.0.0"
    assert version.module.name == "Data Structures in Cloud"
    assert version.artifact.filename == "ds-cloud-v1.0.0.tar.gz"


def test_deployment_relationship(db_session):
    """Verify deployment creation linked to module, version, and user."""
    deployer = User(name="DevOps Engineer", email="ops@college.edu", role="developer")
    db_session.add(deployer)
    db_session.commit()

    module = Module(
        name="Exam Grading Worker",
        description="Background async grading service.",
        owner_id=deployer.id,
        technology="Python / Celery",
        architecture="Worker",
        environment="staging",
        status="active",
    )
    db_session.add(module)
    db_session.commit()

    version = ModuleVersion(
        module_id=module.id,
        version="2.0.0",
        release_notes="Production grading pipeline.",
    )
    db_session.add(version)
    db_session.commit()

    deployment = Deployment(
        module_id=module.id,
        version_id=version.id,
        environment="staging",
        status="running",
        deployed_by=deployer.id,
    )
    db_session.add(deployment)
    db_session.commit()
    db_session.refresh(deployment)

    assert deployment.id is not None
    assert deployment.status == "running"
    assert deployment.module.name == "Exam Grading Worker"
    assert deployment.version.version == "2.0.0"
    assert deployment.deployer.name == "DevOps Engineer"


def test_audit_log_creation(db_session):
    """Verify audit log records."""
    admin = User(name="Auditor", email="auditor@college.edu", role="admin")
    db_session.add(admin)
    db_session.commit()

    log = AuditLog(
        user_id=admin.id,
        action="UPDATE_MODULE_STATUS",
        resource_type="module",
        resource_id="101",
        details="Changed status from draft to review",
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)

    assert log.id is not None
    assert log.user.email == "auditor@college.edu"
    assert log.action == "UPDATE_MODULE_STATUS"


def test_seed_database_execution(db_session):
    """Verify the development database seed function."""
    counts = seed_database(db_session)
    assert counts["users"] >= 2
    assert counts["modules"] >= 2
    assert counts["artifacts"] >= 2
    assert counts["module_versions"] >= 3
    assert counts["deployments"] >= 2
    assert counts["audit_logs"] >= 1


def test_database_url_driver_normalization():
    """Verify that settings.sync_database_url ensures the postgresql+psycopg2 driver."""
    from app.core.config import Settings
    custom_settings = Settings(DATABASE_URL="postgresql://user:pass@127.0.0.1:5433/db")
    assert custom_settings.sync_database_url == "postgresql+psycopg2://user:pass@127.0.0.1:5433/db"

    custom_settings_explicit = Settings(DATABASE_URL="postgresql+psycopg2://user:pass@127.0.0.1:5433/db")
    assert custom_settings_explicit.sync_database_url == "postgresql+psycopg2://user:pass@127.0.0.1:5433/db"

