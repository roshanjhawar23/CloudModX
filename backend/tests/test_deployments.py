import pytest
from io import BytesIO
from app.models.user import User
from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.artifact import Artifact
from app.models.audit_log import AuditLog


def test_deployment_success_with_artifact(client, db_session):
    user = User(name="DevOps Lead", email="devops@college.edu", role="admin")
    db_session.add(user)
    db_session.commit()

    mod = Module(
        name="Payment Service",
        owner_id=user.id,
        technology="Python",
        architecture="Microservice",
        environment="production",
        status="draft",
    )
    db_session.add(mod)
    db_session.commit()

    ver = ModuleVersion(module_id=mod.id, version="1.0.0", release_notes="Initial build")
    db_session.add(ver)
    db_session.commit()

    # Upload artifact
    client.post(
        f"/api/v1/modules/{mod.id}/versions/{ver.id}/artifact",
        files={"file": ("payment-1.0.0.tar.gz", BytesIO(b"binary-content"), "application/gzip")},
    )

    # Trigger deployment
    dep_payload = {
        "module_id": mod.id,
        "version_id": ver.id,
        "environment": "production",
        "deployed_by": user.id,
    }
    res = client.post("/api/v1/deployments", json=dep_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "success"
    assert data["error_message"] is None
    assert data["environment"] == "production"

    # Module promoted to active
    db_session.refresh(mod)
    assert mod.status == "active"

    # Audit log check
    audits = client.get("/api/v1/audit-logs").json()
    actions = [a["action"] for a in audits]
    assert "DEPLOYMENT_SUCCESS" in actions


def test_deployment_failure_without_artifact(client, db_session):
    user = User(name="Dev Lead", email="dev@college.edu", role="developer")
    db_session.add(user)
    db_session.commit()

    mod = Module(
        name="Notification Service",
        owner_id=user.id,
        technology="Node.js",
        architecture="Microservice",
        environment="production",
        status="review",
    )
    db_session.add(mod)
    db_session.commit()

    ver = ModuleVersion(module_id=mod.id, version="0.5.0", release_notes="No artifact version")
    db_session.add(ver)
    db_session.commit()

    # Deploy without uploading artifact
    dep_payload = {
        "module_id": mod.id,
        "version_id": ver.id,
        "environment": "production",
    }
    res = client.post("/api/v1/deployments", json=dep_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "failed"
    assert "artifact missing" in data["error_message"].lower()

    # Audit log check
    audits = client.get("/api/v1/audit-logs").json()
    actions = [a["action"] for a in audits]
    assert "DEPLOYMENT_FAILED" in actions


def test_deployment_rollback_flow(client, db_session):
    user = User(name="Admin", email="admin@college.edu", role="admin")
    db_session.add(user)
    db_session.commit()

    mod = Module(name="Catalog Service", owner_id=user.id, technology="Go", architecture="Microservice", environment="production")
    db_session.add(mod)
    db_session.commit()

    # Version 1.0 (Stable)
    v1 = ModuleVersion(module_id=mod.id, version="1.0.0")
    db_session.add(v1)
    db_session.commit()
    client.post(
        f"/api/v1/modules/{mod.id}/versions/{v1.id}/artifact",
        files={"file": ("cat-1.0.0.tar.gz", BytesIO(b"v1"), "application/gzip")},
    )
    res_dep1 = client.post("/api/v1/deployments", json={"module_id": mod.id, "version_id": v1.id, "environment": "production"})
    assert res_dep1.json()["status"] == "success"

    # Version 2.0 (Broken release)
    v2 = ModuleVersion(module_id=mod.id, version="2.0.0")
    db_session.add(v2)
    db_session.commit()
    client.post(
        f"/api/v1/modules/{mod.id}/versions/{v2.id}/artifact",
        files={"file": ("cat-2.0.0.tar.gz", BytesIO(b"v2"), "application/gzip")},
    )
    # Deploy with simulated failure
    res_dep2 = client.post(
        "/api/v1/deployments",
        json={"module_id": mod.id, "version_id": v2.id, "environment": "production", "simulate_failure": True},
    )
    assert res_dep2.json()["status"] == "failed"

    # Execute Rollback
    rb_res = client.post("/api/v1/deployments/rollback", json={"module_id": mod.id, "environment": "production"})
    assert rb_res.status_code == 201
    rb_data = rb_res.json()
    assert rb_data["status"] == "success"
    assert rb_data["version_id"] == v1.id
    assert "rolled back" in rb_data["error_message"].lower()

    # Verify rollback audit log
    audits = client.get("/api/v1/audit-logs").json()
    actions = [a["action"] for a in audits]
    assert "DEPLOYMENT_ROLLBACK" in actions


def test_rollback_no_history_fails(client, db_session):
    user = User(name="Test User", email="test@college.edu", role="admin")
    db_session.add(user)
    db_session.commit()

    mod = Module(name="Empty Service", owner_id=user.id, technology="Java", architecture="Microservice", environment="production")
    db_session.add(mod)
    db_session.commit()

    rb_res = client.post("/api/v1/deployments/rollback", json={"module_id": mod.id, "environment": "production"})
    assert rb_res.status_code == 400
    assert "no deployment history" in rb_res.json()["detail"].lower()
