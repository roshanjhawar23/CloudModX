# CloudModX Security Model

CloudModX implements defense-in-depth principles tailored for AWS cloud native operations.

## 1. Network Isolation
- **Public Ingress**: Restricted strictly to TCP Port 80 (HTTP) on the EC2 Security Group.
- **Backend Isolation**: FastAPI runs on internal container network (`port 8000`), never exposed directly to the internet.
- **Database Isolation**: PostgreSQL RDS is hosted in dedicated private subnets (`publicly_accessible = false`) with ingress allowed *only* from the EC2 application security group on TCP 5432.
- **SSH Disabled**: Host management is performed exclusively through AWS Systems Manager (SSM) Session Manager using IAM policies. Port 22 is closed.

## 2. Secrets & Identity
- **Zero Static Credentials**: EC2 utilizes an attached IAM Instance Profile with least-privilege policies for S3 bucket access (`s3:PutObject`, `s3:GetObject`, `s3:ListBucket`) and CloudWatch Agent logging.
- **No Secrets in Source Control**: Credentials, connection strings, and encryption keys are injected exclusively via environment variables and excluded via `.gitignore`.
- **RDS Encryption**: Storage encrypted at rest using AWS KMS (`aws/rds` managed key).

## 3. Immutability & Audit Trail
- **Checksum Verification**: Release artifacts generate SHA-256 digests upon S3 ingestion.
- **Tamper-Evident Audit Logging**: Every administrative action (module creation, status transition, artifact upload, deployment execution, failure diagnostic, and rollback) automatically writes immutable audit records to PostgreSQL.
