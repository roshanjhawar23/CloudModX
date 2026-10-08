"""CloudModX Development Database Seeder.

Populates a small, safe development dataset for local testing:
- 1 Admin user, 1 Developer user
- 2 Example cloud-native modules
- Version releases and local artifact records
- Deployments across environments
- Initial system audit log
"""
import sys
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database.session import SessionLocal, engine, Base
from app.models.user import User
from app.models.module import Module
from app.models.artifact import Artifact
from app.models.module_version import ModuleVersion
from app.models.deployment import Deployment
from app.models.audit_log import AuditLog

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("seed")


def seed_database(db: Session) -> dict:
    """Idempotently seed the development database with small baseline dataset."""
    logger.info("Checking existing seed data...")

    # 1. Seed Users
    admin = db.query(User).filter(User.email == "admin@cloudmodx.local").first()
    if not admin:
        admin = User(
            name="Admin User",
            email="admin@cloudmodx.local",
            role="admin",
        )
        db.add(admin)

    developer = db.query(User).filter(User.email == "developer@cloudmodx.local").first()
    if not developer:
        developer = User(
            name="Developer User",
            email="developer@cloudmodx.local",
            role="developer",
        )
        db.add(developer)

    db.flush()

    # 2. Seed Modules
    mod_catalog = db.query(Module).filter(Module.name == "Course Catalog Service").first()
    if not mod_catalog:
        mod_catalog = Module(
            name="Course Catalog Service",
            description="Core curriculum and academic course metadata microservice.",
            owner_id=admin.id,
            technology="Python / FastAPI",
            architecture="Microservice",
            environment="development",
            status="active",
            repository_url="https://github.com/cloudmodx/course-catalog",
        )
        db.add(mod_catalog)

    mod_gateway = db.query(Module).filter(Module.name == "Student Enrollment Gateway").first()
    if not mod_gateway:
        mod_gateway = Module(
            name="Student Enrollment Gateway",
            description="High-throughput admission and semester course enrollment portal.",
            owner_id=developer.id,
            technology="React / Node.js",
            architecture="Serverless Gateway",
            environment="development",
            status="approved",
            repository_url="https://github.com/cloudmodx/enrollment-gateway",
        )
        db.add(mod_gateway)

    db.flush()

    # 3. Seed Artifacts
    art_catalog_1 = db.query(Artifact).filter(
        Artifact.module_id == mod_catalog.id, Artifact.version == "1.0.0"
    ).first()
    if not art_catalog_1:
        art_catalog_1 = Artifact(
            module_id=mod_catalog.id,
            version="1.0.0",
            filename="course-catalog-v1.0.0.tar.gz",
            storage_provider="local",
            storage_path="/var/storage/artifacts/course-catalog-v1.0.0.tar.gz",
            size_bytes=1048576,
            checksum="sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
        db.add(art_catalog_1)

    art_gateway_1 = db.query(Artifact).filter(
        Artifact.module_id == mod_gateway.id, Artifact.version == "0.9.0"
    ).first()
    if not art_gateway_1:
        art_gateway_1 = Artifact(
            module_id=mod_gateway.id,
            version="0.9.0",
            filename="enrollment-gateway-v0.9.0.zip",
            storage_provider="local",
            storage_path="/var/storage/artifacts/enrollment-gateway-v0.9.0.zip",
            size_bytes=2097152,
            checksum="sha256:d82c4220361f5a4404554aa11e8b23be661f7ec4556d33616537ecd673fc2020",
        )
        db.add(art_gateway_1)

    db.flush()

    # 4. Seed Module Versions
    ver_catalog_1 = db.query(ModuleVersion).filter(
        ModuleVersion.module_id == mod_catalog.id, ModuleVersion.version == "1.0.0"
    ).first()
    if not ver_catalog_1:
        ver_catalog_1 = ModuleVersion(
            module_id=mod_catalog.id,
            version="1.0.0",
            release_notes="Initial production-ready release of Course Catalog Service.",
            artifact_id=art_catalog_1.id,
        )
        db.add(ver_catalog_1)

    ver_catalog_2 = db.query(ModuleVersion).filter(
        ModuleVersion.module_id == mod_catalog.id, ModuleVersion.version == "1.1.0"
    ).first()
    if not ver_catalog_2:
        ver_catalog_2 = ModuleVersion(
            module_id=mod_catalog.id,
            version="1.1.0",
            release_notes="Added prerequisite validation and department filtering.",
            artifact_id=None,
        )
        db.add(ver_catalog_2)

    ver_gateway_1 = db.query(ModuleVersion).filter(
        ModuleVersion.module_id == mod_gateway.id, ModuleVersion.version == "0.9.0"
    ).first()
    if not ver_gateway_1:
        ver_gateway_1 = ModuleVersion(
            module_id=mod_gateway.id,
            version="0.9.0",
            release_notes="Beta release for testing semester registration workflows.",
            artifact_id=art_gateway_1.id,
        )
        db.add(ver_gateway_1)

    db.flush()

    # 5. Seed Deployments
    now = datetime.now(timezone.utc)
    dep_1 = db.query(Deployment).filter(
        Deployment.module_id == mod_catalog.id, Deployment.version_id == ver_catalog_1.id
    ).first()
    if not dep_1:
        dep_1 = Deployment(
            module_id=mod_catalog.id,
            version_id=ver_catalog_1.id,
            environment="prod",
            status="success",
            deployed_by=admin.id,
            started_at=now - timedelta(hours=2),
            completed_at=now - timedelta(hours=1, minutes=55),
        )
        db.add(dep_1)

    dep_2 = db.query(Deployment).filter(
        Deployment.module_id == mod_catalog.id, Deployment.version_id == ver_catalog_2.id
    ).first()
    if not dep_2:
        dep_2 = Deployment(
            module_id=mod_catalog.id,
            version_id=ver_catalog_2.id,
            environment="dev",
            status="running",
            deployed_by=developer.id,
            started_at=now - timedelta(minutes=15),
            completed_at=None,
        )
        db.add(dep_2)

    # 6. Seed Audit Log
    log_entry = db.query(AuditLog).filter(AuditLog.action == "INITIALIZE_SEED_DATA").first()
    if not log_entry:
        log_entry = AuditLog(
            user_id=admin.id,
            action="INITIALIZE_SEED_DATA",
            resource_type="system",
            resource_id="seed",
            details="Initial local development seed dataset populated.",
        )
        db.add(log_entry)

    db.commit()
    logger.info("Database seeding completed successfully.")

    return {
        "users": db.query(User).count(),
        "modules": db.query(Module).count(),
        "artifacts": db.query(Artifact).count(),
        "module_versions": db.query(ModuleVersion).count(),
        "deployments": db.query(Deployment).count(),
        "audit_logs": db.query(AuditLog).count(),
    }


def main():
    if SessionLocal is None:
        logger.error("SessionLocal is not initialized. Ensure DATABASE_URL is properly configured.")
        sys.exit(1)

    # Ensure tables exist (or run migrations beforehand)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        counts = seed_database(db)
        logger.info(f"Summary of database records: {counts}")
    except Exception as e:
        logger.error(f"Error while seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
