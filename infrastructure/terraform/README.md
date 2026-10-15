# CloudModX Infrastructure — Terraform

This directory contains the Terraform configuration that provisions CloudModX infrastructure on AWS. For step-by-step provisioning, application deployment and teardown, see **Section 8 of the [main README](../../README.md#8-aws-deployment-cost--teardown)**.

---

## Requirements

- **Terraform:** `>= 1.16` (see `versions.tf`)
- **AWS Provider:** `hashicorp/aws` `~> 6.0`
- **Default region:** `ap-south-1` (Mumbai), configurable with `aws_region`
- **Authentication:** standard AWS CLI credential resolution (`~/.aws/credentials`, `~/.aws/config`, or environment variables). No credentials are stored in this repository.

---

## Managed AWS Resources

### 1. VPC & Networking (`vpc.tf`)
- VPC `10.0.0.0/16` with DNS hostnames and DNS resolution enabled
- 2 public subnets (`10.0.1.0/24`, `10.0.2.0/24`) and 2 private subnets (`10.0.11.0/24`, `10.0.12.0/24`) in the first two Availability Zones of the region
- Internet Gateway with a default route on the public route table
- No NAT Gateway (no hourly cost)

### 2. EC2 Docker Host (`ec2.tf`)
- `t3.small` (2 vCPU, 2 GiB RAM) in public subnet A with a public IPv4 address
- Latest Amazon Linux 2023 x86_64 AMI
- 20 GiB encrypted GP3 root volume
- User data installs Docker Engine, Docker Compose v2, Git and jq, adds `ec2-user` to the `docker` group, and creates `/opt/cloudmodx`
- **Security group:** inbound TCP 80 from anywhere only; SSH (22) is not open; all outbound allowed
- **IAM instance profile:** `AmazonSSMManagedInstanceCore` (Session Manager access) and an inline policy limited to the artifact bucket (`ListBucket`, `GetBucketLocation`, `GetObject`, `PutObject`, `DeleteObject`)

### 3. RDS PostgreSQL (`rds.tf`)
- PostgreSQL 15 on `db.t4g.micro`, Single-AZ, 20 GB encrypted GP3, storage autoscaling disabled
- DB subnet group across both private subnets; `publicly_accessible = false`
- Security group allows TCP 5432 only from the EC2 security group
- Demo-oriented defaults: `backup_retention_period = 0`, `skip_final_snapshot = true`, `deletion_protection = false`
- Master password comes from `db_password` (no default; supply via `terraform.tfvars` or `TF_VAR_db_password`)

### 4. S3 Artifact Storage (`s3.tf`)
- Bucket named `cloudmodx-artifacts-<environment>-<random suffix>`
- SSE-S3 encryption, versioning, full public access block, BucketOwnerEnforced ownership, and a lifecycle rule that aborts incomplete multipart uploads after 7 days
- `force_destroy` is controlled by `artifact_bucket_force_destroy` (default `false`); set it to `true` before `terraform destroy` if the bucket contains objects

### 5. Monitoring (`monitoring.tf`)
- CloudWatch log group `/cloudmodx/<environment>/application` with 7-day retention
- `CloudWatchAgentServerPolicy` attached to the EC2 role (the agent itself is not installed by user data)
- Alarms: EC2 CPU ≥ 80%, EC2 status check failed, RDS CPU ≥ 80%, RDS free storage ≤ 2 GB, RDS connections ≥ 40 (no SNS notification target is configured)

---

## Input Variables

| Variable | Default | Notes |
|:---|:---|:---|
| `db_password` | *(required)* | 12+ letters and digits recommended; avoid `/ @ " # % :` and spaces |
| `aws_region` | `ap-south-1` | |
| `environment` | `development` | Used in names and tags |
| `instance_type` | `t3.small` | |
| `root_volume_size` | `20` | GB |
| `db_instance_class` | `db.t4g.micro` | |
| `db_allocated_storage` | `20` | GB |
| `db_backup_retention_period` | `0` | Days; `0` disables automated backups |
| `artifact_bucket_force_destroy` | `false` | Set `true` before teardown |
| `key_name` | `""` | Optional EC2 key pair; not needed with SSM |

See `variables.tf` for the full list (CIDR ranges, names, prefixes).

## Useful Outputs

`ec2_instance_id`, `ec2_public_ip`, `rds_address`, `rds_endpoint`, `artifact_bucket_name`, `cloudwatch_log_group_name` — see `outputs.tf` for all outputs.

---

## Directory Structure

```text
infrastructure/terraform/
├── .terraform.lock.hcl        # Provider dependency lock file (tracked in git)
├── versions.tf                # Terraform core and provider version requirements
├── provider.tf                # AWS provider configuration and default tags
├── variables.tf               # Input variables
├── vpc.tf                     # VPC, subnets, IGW, route tables
├── ec2.tf                     # EC2 instance, security group, IAM role/profile, Docker bootstrap
├── rds.tf                     # RDS PostgreSQL, DB subnet group, RDS security group
├── s3.tf                      # Artifact bucket, encryption, versioning, lifecycle
├── monitoring.tf              # CloudWatch log group and alarms
├── outputs.tf                 # Output values
├── terraform.tfvars.example   # Copy to terraform.tfvars (gitignored) and set db_password
└── README.md                  # This file
```

---

## Workflow Commands

```bash
terraform fmt        # format files
terraform validate   # check configuration
terraform plan       # preview changes
terraform apply      # create/update resources

# Teardown (empties the artifact bucket first if needed)
terraform apply -var="artifact_bucket_force_destroy=true"
terraform destroy
```
