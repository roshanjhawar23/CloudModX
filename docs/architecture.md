# CloudModX Architecture

CloudModX is a lightweight AWS-native Internal Developer Platform (IDP) designed for managing the full lifecycle of cloud-native modules, versions, release packages, deployments, and audit trails.

## System Overview

```
                          [ Internet / Browser ]
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

## Core Components

1. **Frontend**:
   - **Stack**: React 18, Vite, Tailwind CSS, Lucide Icons.
   - **Hosting**: Containerized Nginx serving static assets and reverse-proxying `/api/` traffic to the backend on internal bridge network.
   - **Ingress**: Exposed on host port `80:80`.

2. **Backend**:
   - **Stack**: FastAPI (Python 3.11), SQLAlchemy ORM, Pydantic v2, psycopg2.
   - **Network**: Bound strictly to internal container network (no host port binding).
   - **Services**: RESTful CRUD endpoints for modules, semantic version releases, multipart S3 artifact upload, deployment orchestration, and audit logging.

3. **Database (RDS)**:
   - **Engine**: PostgreSQL 15 (`db.t4g.micro`, Single-AZ, gp3 storage, storage encrypted via KMS).
   - **Placement**: Private DB subnet group across two Availability Zones (`ap-south-1a`, `ap-south-1b`).
   - **Access**: Ingress restricted to EC2 security group only on port 5432.

4. **Storage (S3)**:
   - **Bucket**: `cloudmodx-artifacts-development-7e20711b318423260d00ea711f`.
   - **Authentication**: AWS IAM EC2 Instance Profile (`AmazonSSMManagedInstanceCore` + S3 Put/Get permissions). No static credentials in code or containers.

5. **Observability (CloudWatch)**:
   - **Agent**: `amazon-cloudwatch-agent` collecting Docker and system logs to `/cloudmodx/development/application`.
   - **Alarms**: High CPU (EC2/RDS), Status Checks, Free Storage, and RDS Connection metrics.
