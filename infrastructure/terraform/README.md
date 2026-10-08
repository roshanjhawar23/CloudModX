# CloudModX Infrastructure — Terraform

This directory contains the HashiCorp Terraform configuration for provisioning CloudModX cloud-native infrastructure on Amazon Web Services (AWS).

---

## Current Status: Phase 8 (EC2 + Docker Host Deployment — Hardened)

- **Terraform Version Requirement:** `>= 1.16`
- **AWS Provider:** `hashicorp/aws` constraint `~> 6.0`
- **Target AWS Region:** `ap-south-1` (Mumbai)
- **Authentication:** Standard AWS CLI credential resolution (`~/.aws/credentials`, `~/.aws/config`, or environment variables). No hardcoded credentials.

---

## Managed AWS Resources

### 1. EC2 Docker Application Host (`ec2.tf`)
- **Instance Type:** `t3.small` (2 vCPU, 2 GiB RAM, cost-effective for Docker runtime and container builds)
- **Placement:** Public Subnet A (`subnet-0300a2f74a6d4850f` / `ap-south-1a`) with public IPv4 address
- **AMI:** Latest Amazon Linux 2023 (`al2023-ami-2023.*-x86_64`)
- **Storage:** 20 GiB GP3 encrypted root volume
- **Terminal Access:** Zero-trust AWS Systems Manager Session Manager (SSH port 22 closed)
- **Bootstrap (User Data):**
  - Installs Docker Engine, Git, curl, jq
  - Installs Docker Compose v2 CLI plugin
  - Enables and starts `docker.service`
  - Adds `ec2-user` to `docker` group
  - Sets up `/opt/cloudmodx` working directory
- **IAM Instance Profile:**
  - `AmazonSSMManagedInstanceCore` for secure browser/CLI terminal access via AWS Systems Manager Session Manager
  - Scoped S3 policy pinned to the exact Terraform S3 bucket ARN (`aws_s3_bucket.artifacts.arn`)

### 2. Security Group (`aws_security_group.app_server`)
- **Port 22 (SSH):** **Disabled/Removed** — all administrative operations use AWS SSM Session Manager
- **Port 80 (HTTP):** Public web traffic (`0.0.0.0/0`)
- **Port 3000 (React UI):** Temporary demo direct access (`var.app_access_cidr`)
- **Port 8000 (FastAPI):** Temporary demo direct API access (`var.app_access_cidr`)
- **All Egress:** Outbound access for package updates, Docker Hub image pulls, and AWS API calls

### 3. VPC & Networking (`vpc.tf`)
- **VPC CIDR:** `10.0.0.0/16` with DNS hostnames and DNS resolution enabled
- **Subnets:** 2 Public subnets (`10.0.1.0/24`, `10.0.2.0/24`) and 2 Private subnets (`10.0.11.0/24`, `10.0.12.0/24`) across `ap-south-1a` and `ap-south-1b`
- **Internet Gateway:** Attached to VPC with default route on public route table
- **NAT Gateway:** None (zero hourly cost)

### 4. S3 Artifact Storage (`s3.tf`)
- **Bucket:** Dedicated S3 bucket for module artifacts with SSE-S3 encryption, versioning, public access block, and multipart cleanup lifecycle rules

---

## Directory Structure

```text
infrastructure/terraform/
├── .terraform.lock.hcl   # Provider dependency lock file (tracked in git)
├── versions.tf           # Terraform core and provider version requirements
├── provider.tf           # AWS provider configuration and default tags
├── variables.tf          # Input variable definitions (region, environment, CIDRs, EC2)
├── ec2.tf                # EC2 instance, security group, IAM role/profile, Docker bootstrap
├── vpc.tf                # VPC, Subnets, IGW, Route Tables, and Associations
├── s3.tf                 # S3 bucket, encryption, versioning, and security policies
├── outputs.tf            # Output definitions (VPC ID, subnets, EC2 IP, S3 ARN)
└── README.md             # This documentation
```

---

## Workflow Commands

### 1. Format configuration
```bash
terraform fmt
```

### 2. Validate syntax and configuration
```bash
terraform validate
```

### 3. Plan infrastructure changes
```bash
terraform plan
```
