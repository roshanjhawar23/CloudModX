# CloudModX

> Lightweight AWS-native Internal Developer Platform (IDP) and Module Lifecycle Management System.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![React](https://img.shields.io/badge/React-18-61dafb)
![AWS Region](https://img.shields.io/badge/AWS%20Region-ap--south--1-orange)
![EC2](https://img.shields.io/badge/Amazon%20EC2-t3.small-blue)
![Database](https://img.shields.io/badge/Amazon%20RDS-PostgreSQL%2015-blue)

---

## 1. Project Purpose

CloudModX is an Internal Developer Platform for registering, versioning, packaging, deploying and auditing software modules. It gives developers and platform engineers one dashboard to manage module lifecycles, store release artifacts in Amazon S3 (or on local disk during development), track deployments per environment, and roll back to the last good version when a deployment fails.

> **Scope note:** Deployments in CloudModX are a tracked workflow. The platform validates the release artifact, records the deployment state, promotes the module and writes an audit trail. It does not push code to a separate runtime target. Failures can be produced on demand with `simulate_failure` for demos and testing.

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
| **Amazon VPC** | Network Isolation | Custom VPC `10.0.0.0/16` with 2 public and 2 private subnets across the first 2 Availability Zones of the region. |
| **Amazon EC2** | Application Host | `t3.small` (2 vCPU, 2 GB RAM, 20 GB GP3 encrypted root), Amazon Linux 2023, Docker + Compose installed at boot. Managed via AWS SSM (no SSH). |
| **Amazon RDS** | Production Relational DB | `db.t4g.micro` PostgreSQL 15, Single-AZ, 20 GB GP3 storage (encrypted), private subnets only. |
| **Amazon S3** | Artifact Storage | Versioned, encrypted (SSE-S3), public-access-blocked bucket for release artifacts. |
| **AWS IAM** | Identity & Access | EC2 instance role scoped to the artifact bucket, plus SSM and CloudWatch agent policies (no static keys). |
| **CloudWatch** | Observability | Log group `/cloudmodx/<environment>/application` (7-day retention) and alarms for EC2 CPU/status checks and RDS CPU/storage/connections. *Shipping container logs into the log group requires installing the CloudWatch agent on the instance; this is not automated yet.* |

---

## 3. Module Lifecycle & Deployment Workflow

### Lifecycle Stages
```
  [ Draft ] ──> [ Review ] ──> [ Approved ] ──> [ Active ] ──> [ Archived ]
```
Status can be changed with `PATCH /api/v1/modules/{id}/status`. A successful deployment automatically promotes a `draft`, `review` or `approved` module to `active`.

### Deployment State Flow
1. **Creation**: `POST /api/v1/deployments` with `module_id` and `version_id`. If `environment` is omitted, the module's own environment is used. The record starts in `running` state.
2. **Artifact Validation**: The target `ModuleVersion` must have an uploaded artifact (`POST /api/v1/modules/{id}/versions/{version_id}/artifact`).
3. **Success**: If the artifact exists, the deployment is marked `success` and the module is promoted to `active`.
4. **Failure**: If the artifact is missing, or the request sets `"simulate_failure": true`, the deployment is marked `failed` and the reason is stored in `error_message`.
5. **Rollback**: `POST /api/v1/modules/{id}/rollback` (or `POST /api/v1/deployments/rollback`) finds the most recent successful deployment of a different version in the same environment and records a new `success` deployment pointing at that version. The environment can be passed as `?environment=...` or in a JSON body; if omitted, the module's environment is used.
6. **Audit Trail**: Actions write a record to the `audit_logs` table: `CREATE_MODULE`, `UPDATE_MODULE_STATUS`, `CREATE_VERSION`, `UPLOAD_ARTIFACT`, `DEPLOYMENT_SUCCESS`, `DEPLOYMENT_FAILED`, `DEPLOYMENT_ROLLBACK` (plus `INITIALIZE_SEED_DATA` from the seed script). View them with `GET /api/v1/audit-logs`.

---

## 4. Local Development Run Instructions

### Prerequisites
- **Git**
- **Docker Desktop** (with Docker Compose v2+) — for the Quick Start, or just for PostgreSQL in the host-run setup
- **Python 3.11+** and **Node.js 18+** & npm — only for the host-run setup
- **Terraform v1.16+** & AWS CLI v2 — only for AWS deployment (Section 8)

### Network Ports & URLs

| Service | Container Port | Host Port | Local Access URL |
|:---|:---|:---|:---|
| **Frontend UI (Nginx)** | `80` | `80` | `http://localhost` |
| **Backend API (FastAPI)** | `8000` | `8000` | `http://localhost:8000` (Docs: `http://localhost:8000/docs`) |
| **API via Nginx Proxy** | — | `80` | `http://localhost/api/health` |
| **PostgreSQL Database** | `5432` | `5433` | `127.0.0.1:5433` (avoids conflict with a local PostgreSQL on 5432) |

### Quick Start with Docker Compose (Recommended)

1. **Clone the repository and create the environment file**:
   ```bash
   git clone https://github.com/roshanjhawar23/CloudModX.git
   cd CloudModX
   cp .env.example .env
   ```
   The defaults in `.env` work as-is for local development. Inside Compose the backend connects to PostgreSQL at `db:5432`, and uploaded artifacts are stored on local disk because `ARTIFACT_BUCKET_NAME` is empty.

2. **Start the stack**:
   ```bash
   docker compose up --build -d
   ```

3. **Run migrations and seed sample data**:
   ```bash
   docker compose exec backend alembic upgrade head
   docker compose exec backend python -m app.database.seed
   ```
   The seed script is safe to run more than once.

4. **Verify application health**:
   ```bash
   curl -f http://localhost:8000/api/health
   # Or via the Nginx proxy:
   curl -f http://localhost/api/health
   ```
   Open `http://localhost` in your browser to view the CloudModX dashboard.

5. **Stop services**:
   ```bash
   docker compose down
   # Also delete the database volume:
   docker compose down -v
   ```

---

### Host-Run Development (Without Docker for Backend/Frontend)

Run Python and React directly on your machine, using Docker only for PostgreSQL.

1. **Start only PostgreSQL** (from the repository root):
   ```bash
   cp .env.example .env      # if you have not already
   docker compose up -d db
   ```

2. **Backend setup**:
   ```bash
   cd backend
   cp .env.example .env      # already points at 127.0.0.1:5433; no edits needed
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   alembic upgrade head
   python -m app.database.seed
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   > When running from inside `backend/`, only `backend/.env` is read, not the root `.env`. If you change the database password in the root `.env`, update `DATABASE_URL` in `backend/.env` to match.

3. **Frontend setup** (in a second terminal, from the repository root):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open `http://localhost:5173`. The Vite dev server proxies `/api` calls to `http://localhost:8000`.

### Configuration Reference

| Variable | Default | Purpose |
|:---|:---|:---|
| `ENVIRONMENT` | `development` | Set to `production` to enable strict config validation. |
| `SECRET_KEY` | dev placeholder | Must be a random string of 32+ characters in production. Generate one with `python -c "import secrets; print(secrets.token_hex(32))"`. |
| `DATABASE_URL` | local PostgreSQL | SQLAlchemy URL, e.g. `postgresql+psycopg2://user:pass@host:5432/db`. |
| `ARTIFACT_BUCKET_NAME` | *(empty)* | Empty = store artifacts on local disk (`/tmp/cloudmodx-artifacts`). Set to **your own** S3 bucket to use S3. |
| `AWS_REGION` | `ap-south-1` | Region of the artifact bucket. |
| `SQL_ECHO` | `false` | `true` logs every SQL statement. |

---

## 5. Testing & Verification

### Backend Tests
The pytest suite covers database models, the seed script, module and version APIs, artifact uploads, deployment success/failure, rollback and health endpoints.

```bash
# From the repository root, with backend dependencies installed
python -m pytest backend/tests -v
```
All 21 tests run against an isolated SQLite in-memory database with local artifact storage, so no PostgreSQL or AWS account is needed.

### Frontend Production Build
```bash
cd frontend
npm install
npm run build
```

---

## 6. Troubleshooting

- **Port 80 conflict on host**:
  IIS, Apache or Skype may already use port 80. In `docker-compose.yml`, change the `frontend` port from `"80:80"` to `"3000:80"` and open `http://localhost:3000`.
- **Port 5433 conflict**:
  Change `"5433:5432"` under the `db` service in `docker-compose.yml`, and update the port in `backend/.env` to match.
- **Health check shows "degraded"**:
  The API is up but cannot reach PostgreSQL. Run `docker compose ps` and `docker compose logs db` to check the database container.
- **Backend connection refused**:
  Inside Docker Compose the backend uses `db:5432`. Only processes running on your host use `127.0.0.1:5433`.
- **Backend refuses to start with "Production configuration error"**:
  `ENVIRONMENT=production` requires a real `SECRET_KEY` (32+ random characters, no placeholder text) and a `DATABASE_URL` that is not localhost.

---

## 7. Security Model & Production Hardening

- **Restricted public surface**: Only TCP port 80 is open to the internet on EC2.
- **Internal API**: FastAPI listens on port 8000 inside the Docker network; Nginx proxies `/api/` to it.
- **Private database**: RDS sits in private subnets with `publicly_accessible = false` and only accepts TCP 5432 from the EC2 security group.
- **Production validation**: With `ENVIRONMENT=production`, startup fails unless `SECRET_KEY` is at least 32 characters with no placeholder text and `DATABASE_URL` points to a non-localhost database.
- **No committed credentials**: `.env` and `terraform.tfvars` are gitignored. Secrets are supplied through those files or environment variables (`TF_VAR_db_password`).
- **No open SSH**: Port 22 is closed; instance access is through AWS Systems Manager Session Manager.
- **Authentication**: The API does not yet implement user login or authorization. Do not expose a deployment publicly with real data until authentication is added.

---

## 8. AWS Deployment, Cost & Teardown

> Deploying creates billable AWS resources (EC2, RDS, S3, CloudWatch). Destroy them when you are done (see Teardown).

### 8.1 Provision Infrastructure with Terraform

Requirements: Terraform **v1.16+**, AWS CLI v2 configured with credentials (`aws configure`), and permission to create VPC, EC2, RDS, S3, IAM and CloudWatch resources.

1. **Initialize Terraform**:
   ```bash
   cd infrastructure/terraform
   terraform init
   ```

2. **Set the database password**:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```
   Edit `terraform.tfvars` and set `db_password`. Use 12+ letters and digits only; symbols such as `/ @ " # % :` or spaces break the database URL. `terraform.tfvars` is gitignored. Alternatively:
   ```bash
   export TF_VAR_db_password="YourLongPassword123"
   ```

3. **Plan and apply** (RDS creation takes about 5–10 minutes):
   ```bash
   terraform plan
   terraform apply
   ```

4. **Note the outputs** you will need next:
   ```bash
   terraform output ec2_instance_id
   terraform output ec2_public_ip
   terraform output rds_address
   terraform output artifact_bucket_name
   ```

### 8.2 Deploy the Application on EC2

Terraform creates an empty Docker host. These steps put CloudModX on it.

1. **Open a shell on the instance** with SSM, either in the AWS Console (EC2 → instance → Connect → Session Manager) or from your machine (requires the [Session Manager plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)):
   ```bash
   aws ssm start-session --target <ec2_instance_id> --region ap-south-1
   ```
   Wait 2–3 minutes after `terraform apply` for the boot script to finish installing Docker.

2. **Get the code**:
   ```bash
   sudo su - ec2-user
   cd /opt/cloudmodx
   git clone https://github.com/roshanjhawar23/CloudModX.git .
   ```

3. **Create the production `.env`**, replacing the values in `< >` with your Terraform outputs and password:
   ```bash
   cat > .env <<EOF
   ENVIRONMENT=production
   SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
   DATABASE_URL=postgresql+psycopg2://cloudmodx_user:<db_password>@<rds_address>:5432/cloudmodx_db
   ARTIFACT_BUCKET_NAME=<artifact_bucket_name>
   AWS_REGION=ap-south-1
   EOF
   ```

4. **Build and start the frontend and backend** (`--no-deps` skips the local PostgreSQL container, since RDS is used):
   ```bash
   docker compose up -d --build --no-deps backend frontend
   ```

5. **Create the schema and (optionally) seed sample data**:
   ```bash
   docker compose exec backend alembic upgrade head
   docker compose exec backend python -m app.database.seed
   ```

6. **Verify**: open `http://<ec2_public_ip>` in your browser, or run `curl http://<ec2_public_ip>/api/health`. It should report `"database_connected": true`.

To update later: `git pull`, then repeat step 4.

### Cost-Conscious Design

- **No NAT Gateway** (~$32/month saved): the EC2 host sits in a public subnet and reaches RDS directly inside the VPC.
- **No Application Load Balancer** (~$16/month saved): Nginx on the instance serves the UI and proxies the API.
- **Graviton RDS tier**: `db.t4g.micro` is among the cheapest RDS PostgreSQL classes.
- **No automated RDS backups by default** (`db_backup_retention_period = 0`) to keep demo costs down. Increase it for real data.

### Teardown (Destroy All AWS Resources)

The artifact bucket is protected from deletion by default. If you uploaded any artifacts, allow Terraform to empty it first:

```bash
cd infrastructure/terraform
terraform apply -var="artifact_bucket_force_destroy=true"
terraform destroy
```
This removes the EC2 instance, RDS instance (no final snapshot is kept), S3 bucket and its contents, security groups, IAM role, VPC and CloudWatch resources.

---

## 9. Documentation Index

- [Architecture Guide](docs/architecture.md)
- [Deployment & Rollback Workflow](docs/deployment-flow.md)
- [Database Models & Schema](docs/database.md)
- [Security & Isolation Model](docs/security.md)
- [Demo Checklist & Verification Evidence](docs/demo-evidence.md)
- [Terraform Infrastructure](infrastructure/terraform/README.md)
