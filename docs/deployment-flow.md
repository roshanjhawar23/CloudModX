# Deployment & Rollback Workflow

CloudModX provides a deterministic state machine for deploying and rolling back cloud module releases.

## Deployment State Machine

```
[ New Deployment Request ]
            |
            v
       ( PENDING )
            |
            v
       ( RUNNING )
            |
    +-------+-------+
    | Check Artifact|
    +-------+-------+
       /         \
 [Artifact Exists]|          |[Missing / Invalid]
      v           |          v
 ( SUCCESS )      |     ( FAILED )
      |           |          |
 [Promote Module] |     [Capture Diagnostic Error]
      |           |          |
 [Audit Log]      |     [Audit Log]
```

## Lifecycle Stages

1. **Module Creation**:
   - Initial state: `draft`.
   - Transitions allowed: `draft` → `review` → `active` → `archived`.

2. **Version Registration**:
   - Semantic versioning (e.g. `v1.0.0`, `v1.1.0`).
   - Tracks release notes and changelogs.

3. **Artifact Upload**:
   - Multi-part upload streamed to S3 via backend.
   - Computes SHA-256 checksum and exact byte count.
   - Attaches artifact ID to corresponding `ModuleVersion`.

4. **Deployment Execution**:
   - Validates that target version has a verified package artifact.
   - If artifact is missing or validation fails:
     - Sets deployment status to `failed`.
     - Records explicit error reason in `error_message`.
     - Logs `DEPLOYMENT_FAILED` in `audit_logs`.
   - If artifact exists:
     - Sets deployment status to `success`.
     - Promotes module status to `active`.
     - Logs `DEPLOYMENT_SUCCESS` in `audit_logs`.

5. **Rollback Execution**:
   - Endpoint: `POST /api/v1/modules/{id}/rollback` or `POST /api/v1/deployments/rollback`.
   - Discovers deployment history for the module & target environment.
   - Identifies the last verified successful deployment with a previous version.
   - Creates a new rollback deployment record pointing to that target version with status `success`.
   - Records `DEPLOYMENT_ROLLBACK` with source and target release details.
