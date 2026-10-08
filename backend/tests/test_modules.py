import pytest
from app.models.user import User
from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.audit_log import AuditLog


def test_list_modules_empty(client):
    response = client.get("/api/v1/modules")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get_module(client, db_session):
    user = User(name="Faculty Lead", email="faculty@college.edu", role="admin")
    db_session.add(user)
    db_session.commit()

    payload = {
        "name": "Cloud Security Framework",
        "description": "Enterprise cloud security governance and compliance",
        "technology": "Python / FastAPI",
        "architecture": "Serverless",
        "environment": "development",
        "status": "draft",
        "repository_url": "https://github.com/cloudmodx/cloud-sec",
        "owner_id": user.id,
    }

    response = client.post("/api/v1/modules", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Cloud Security Framework"
    assert data["status"] == "draft"
    module_id = data["id"]

    # Verify AuditLog created
    audit = db_session.query(AuditLog).filter(AuditLog.resource_id == str(module_id)).first()
    assert audit is not None
    assert audit.action == "CREATE_MODULE"

    # Get module detail
    detail_res = client.get(f"/api/v1/modules/{module_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == module_id
    assert detail_data["versions"] == []


def test_update_module_status(client, db_session):
    user = User(name="Admin", email="admin@test.local", role="admin")
    db_session.add(user)
    db_session.commit()

    mod = Module(
        name="Telemetry Pipeline",
        owner_id=user.id,
        technology="Go",
        architecture="Microservice",
        environment="development",
        status="draft",
    )
    db_session.add(mod)
    db_session.commit()

    # Valid status change
    res = client.patch(f"/api/v1/modules/{mod.id}/status", json={"status": "approved"})
    assert res.status_code == 200
    assert res.json()["status"] == "approved"

    # Invalid status change
    res_bad = client.patch(f"/api/v1/modules/{mod.id}/status", json={"status": "invalid_status"})
    assert res_bad.status_code == 400


def test_create_version_and_upload_artifact(client, db_session):
    user = User(name="Developer", email="dev@test.local", role="developer")
    db_session.add(user)
    db_session.commit()

    mod = Module(
        name="Payment Gateway",
        owner_id=user.id,
        technology="Node.js",
        architecture="Serverless",
        environment="development",
        status="draft",
    )
    db_session.add(mod)
    db_session.commit()

    # Create version
    v_res = client.post(
        f"/api/v1/modules/{mod.id}/versions",
        json={"version": "1.0.0", "release_notes": "Initial launch"},
    )
    assert v_res.status_code == 201
    v_data = v_res.json()
    version_id = v_data["id"]
    assert v_data["version"] == "1.0.0"

    # Upload mock artifact
    file_bytes = b"sample artifact content for testing"
    files = {"file": ("package.tar.gz", file_bytes, "application/gzip")}
    a_res = client.post(
        f"/api/v1/modules/{mod.id}/versions/{version_id}/artifact",
        files=files,
    )
    assert a_res.status_code == 201
    a_data = a_res.json()
    assert a_data["filename"] == "package.tar.gz"
    assert a_data["size_bytes"] == len(file_bytes)

    # Verify version now has artifact attached
    mod_detail = client.get(f"/api/v1/modules/{mod.id}").json()
    assert len(mod_detail["versions"]) == 1
    assert mod_detail["versions"][0]["artifact_id"] == a_data["id"]
