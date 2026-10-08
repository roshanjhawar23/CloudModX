# CloudModX Demo Checklist & Verification Evidence

This checklist proves the end-to-end functionality of CloudModX on live AWS infrastructure (`EC2: 13.233.167.187`, `RDS: PostgreSQL 15`, `S3: Artifact Storage`).

## 1. Demo Walkthrough Sequence

| Step | Action | UI Location / Endpoint | Expected Result | Verified Status |
|:---|:---|:---|:---|:---:|
| 1 | **Dashboard Overview** | `http://<EC2_IP>/` | Real-time health metrics, RDS connection, recent audit stream | ✅ PASS |
| 2 | **API Health Probe** | `GET /api/health` | HTTP 200 `healthy`, `database_connected: true` | ✅ PASS |
| 3 | **Create Module** | `POST /api/v1/modules` | Module created in `draft` status, Audit logged | ✅ PASS |
| 4 | **Create Version** | `POST /api/v1/modules/{id}/versions` | Semantic version registered (e.g. `v1.0.0`) | ✅ PASS |
| 5 | **Upload Artifact** | `POST /api/v1/modules/{id}/versions/{vid}/artifact` | Multipart upload stored in S3, SHA-256 computed | ✅ PASS |
| 6 | **Deploy Success** | `POST /api/v1/deployments` | Status `success`, module promoted to `active` | ✅ PASS |
| 7 | **Failed Deployment** | `POST /api/v1/deployments` (no artifact) | Status `failed`, diagnostic message captured | ✅ PASS |
| 8 | **Inspect Diagnostics** | `GET /api/v1/modules/{id}` | Error details displayed in pipeline execution table | ✅ PASS |
| 9 | **Rollback Release** | `POST /api/v1/modules/{id}/rollback` | Status `success`, previous stable version restored | ✅ PASS |
| 10 | **Audit Trail Review** | `GET /api/v1/audit-logs` | Chronological audit history of all actions | ✅ PASS |

## 2. Live API Verification Commands

```bash
# 1. Health Verification
curl -s http://<EC2_IP>/api/health

# 2. Create Module
curl -s -X POST http://<EC2_IP>/api/v1/modules \
  -H "Content-Type: application/json" \
  -d '{"name":"Billing-Service","technology":"Go","architecture":"Microservice","environment":"production"}'

# 3. Create Version
curl -s -X POST http://<EC2_IP>/api/v1/modules/<MODULE_ID>/versions \
  -H "Content-Type: application/json" \
  -d '{"version":"v1.0.0","release_notes":"Initial stable release"}'

# 4. Upload Artifact to S3
curl -s -X POST http://<EC2_IP>/api/v1/modules/<MODULE_ID>/versions/<VERSION_ID>/artifact \
  -F "file=@package.tar.gz"

# 5. Execute Deployment
curl -s -X POST http://<EC2_IP>/api/v1/deployments \
  -H "Content-Type: application/json" \
  -d '{"module_id":<MODULE_ID>,"version_id":<VERSION_ID>,"environment":"production"}'

# 6. Execute Rollback
curl -s -X POST http://<EC2_IP>/api/v1/modules/<MODULE_ID>/rollback \
  -H "Content-Type: application/json" \
  -d '{"environment":"production"}'

# 7. Query Audit Logs
curl -s "http://<EC2_IP>/api/v1/audit-logs?limit=10"
```
