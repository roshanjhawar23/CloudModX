# CloudModX

> Lightweight AWS-native Internal Developer Platform (IDP) and Module Lifecycle Management System.

[![Backend Tests](https://img.shields.io/badge/pytest-20%20passed-emerald)]()
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![AWS Region](https://img.shields.io/badge/AWS%20Region-ap--south--1-orange)]()
[![EC2](https://img.shields.io/badge/Amazon%20EC2-t3.small-blue)]()
[![Database](https://img.shields.io/badge/Amazon%20RDS-PostgreSQL%2015-blue)]()

---

## 1. Project Purpose

CloudModX is an Internal Developer Platform designed to streamline how cloud-native software modules are registered, versioned, packaged, deployed, and audited across target environments. It provides developers and platform engineers with a unified dashboard to manage module lifecycles, enforce deployment health checks, store release artifacts in Amazon S3, and trigger instantaneous rollbacks when failures occur.

---

## 2. Architecture & AWS Specifications

```
                           [ Web Browser / Client ]
                                      |
                                   TCP 80 (HTTP)
                                      v
                        +---------------------------+
                        |   Amazon EC2 (t3.small)   |
                        |                           |
                        |   +-------------------+   |
                        |   |   React + Nginx   |   |
                        |   |  (Port 80 Ingress)|   |
                        |   +---------+---------+   |
                        |             | (Internal)  |
                        |             v             |
                        |   +-------------------+   |
                        |   |  FastAPI Backend  |   |
                        |   |    (Port 8000)    |   |
                        |   +----+--------+-----+   |
                        +--------|--------|---------+
                                 |        |
              IAM Role (boto3)   |        |  PostgreSQL TCP 5432
        +------------------------+        +--------------------------+
        |                                                            |
        v                                                            v
 +-----------------------+                         +----------------------------------+
 |    Amazon S3 Bucket   |                         |     Amazon RDS PostgreSQL 15     |
 | (Release Artifacts)   |                         |  (Private Subnets, Encrypted)    |
 +-----------------------+                         +----------------------------------+
```

### AWS Infrastructure Services

| Service | Role in CloudModX | Configuration Details |
|:---|:---|:---|
| **Amazon VPC** | Network Isolation | Custom VPC `10.0.0.0/16` across 2 Availability Zones (`ap-south-1a`, `ap-south-1b`). |
| **Amazon EC2** | Application Host | `t3.small` (2 vCPU, 2 GB RAM, 20 GB GP3 encrypted root) running Docker container stack (Nginx + FastAPI). Managed via AWS SSM. |
| **Amazon RDS** | Production Relational DB | `db.t4g.micro` PostgreSQL 15, Single-AZ, 20 GB GP3 storage (KMS encrypted), private subnets only. |
| **Amazon S3** | Package Storage | Bucket for versioned multi-part tarball/zip build artifacts. |
| **AWS IAM** | Identity & Access | Least-privilege EC2 Instance Role for S3 and CloudWatch (no static keys). |
| **CloudWatch** | Observability | Unified logging group (`/cloudmodx/development/application`) + CPU/Storage/Connection alarms. |

---

## 3. Module Lifecycle & Deployment Engine

### Lifecycle Stages
```
  [ Draft ]  ──>  [ Review ]  ──>  [ Active ]  ──>  [ Archived ]
```

### Deployment State Flow
1. **Creation**: Triggered via `POST /api/v1/deployments`. Initial state starts as `pending` / `running`.
2. **Artifact Validation**: System checks that the target `ModuleVersion` has a valid release artifact attached in Amazon S3.
3. **Success State**: If artifact exists, deployment completes with `status: success` and automatically promotes module to `active`.
4. **Failure State & Diagnostics**: If artifact is missing or health checks fail, deployment is marked `status: failed`, capturing actionable diagnostics in `error_message`.
5. **Rollback Engine**: 1-click Rollback (`POST /api/v1/modules/{id}/rollback`) detects the last verified stable release in history and redeploys it immediately.
6. **Audit Trail**: Every action (`CREATE_MODULE`, `UPLOAD_ARTIFACT`, `DEPLOYMENT_SUCCESS`, `DEPLOYMENT_FAILED`, `DEPLOYMENT_ROLLBACK`) generates immutable PostgreSQL audit records.

---

## 4. Security Model

- **Restricted Public Surface**: Only TCP Port 80 is open to the public on EC2.
- **Internal Microservices**: FastAPI runs on port 8000 internally inside the Docker network.
- **Private Database**: RDS is located in private subnets with no public IP (`publicly_accessible = false`) and only accepts TCP 5432 from the EC2 Security Group.
- **Zero Hardcoded Secrets**: DB passwords, API keys, and configurations are injected via environment variables. IAM Instance Profiles authenticate S3 and CloudWatch.
- **Zero Open SSH**: Port 22 is disabled. Management is done via AWS Systems Manager Session Manager.

---

## 5. Cost-Conscious Design

CloudModX is optimized for cost efficiency without sacrificing cloud-native architecture principles:
- **Zero NAT Gateways**: Avoids managed gateway overhead by placing the EC2 application host in the public subnet while keeping RDS isolated in private subnets with direct internal routing.
- **Zero ALB/ELB overhead**: Nginx reverse proxy running directly on EC2 handles edge routing.
- **ARM64 Graviton RDS**: `db.t4g.micro` provides high performance with lower compute cost.
- **Single-AZ Development Tier**: RDS and EC2 provisioned in Single-AZ with automated KMS encryption.

---

## 6. Local Development Run Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Docker & Docker Compose (optional for local database)

### Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python -m pytest -v
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Run Full Stack with Docker
```bash
docker compose up -d
```
Access the application at `http://localhost:3000` (or `http://localhost:80` via Nginx).

---

## 7. AWS Deployment Overview

Deployments to AWS EC2 are fully automated using AWS Systems Manager (SSM) and Amazon S3:

1. **Package Bundle**:
   ```bash
   tar -czf cloudmodx-deploy.tar.gz --exclude='.git' --exclude='node_modules' --exclude='.env' .
   ```
2. **Upload to S3**:
   ```bash
   aws s3 cp cloudmodx-deploy.tar.gz s3://<ARTIFACT_BUCKET>/deploy/cloudmodx-deploy.tar.gz
   ```
3. **Execute Deployment via SSM**:
   AWS SSM pulls the package, extracts it into `/opt/cloudmodx`, runs Docker Compose builds, and performs health verification probes.

---

## 8. Documentation Index

- [Architecture Guide](docs/architecture.md)
- [Deployment & Rollback Workflow](docs/deployment-flow.md)
- [Database Models & Schema](docs/database.md)
- [Security & Isolation Model](docs/security.md)
- [Demo Checklist & Verification Evidence](docs/demo-evidence.md)
