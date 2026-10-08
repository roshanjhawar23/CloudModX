variable "aws_region" {
  description = "The AWS region to deploy CloudModX infrastructure into"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Deployment environment name (e.g., development, staging, production)"
  type        = string
  default     = "development"
}

variable "project_name" {
  description = "Project name identifier for resource tagging and naming"
  type        = string
  default     = "CloudModX"
}

variable "artifact_bucket_prefix" {
  description = "Prefix for the S3 artifact storage bucket name (AWS will append a unique suffix)"
  type        = string
  default     = "cloudmodx-artifacts"
}

# Networking Variables
variable "vpc_cidr" {
  description = "CIDR block for the CloudModX VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_a_cidr" {
  description = "CIDR block for Public Subnet A (AZ 1)"
  type        = string
  default     = "10.0.1.0/24"
}

variable "public_subnet_b_cidr" {
  description = "CIDR block for Public Subnet B (AZ 2)"
  type        = string
  default     = "10.0.2.0/24"
}

variable "private_subnet_a_cidr" {
  description = "CIDR block for Private Subnet A (AZ 1)"
  type        = string
  default     = "10.0.11.0/24"
}

variable "private_subnet_b_cidr" {
  description = "CIDR block for Private Subnet B (AZ 2)"
  type        = string
  default     = "10.0.12.0/24"
}

# Compute / EC2 Variables
variable "instance_type" {
  description = "EC2 instance type for the CloudModX Docker host (t3.small provides 2GB RAM suitable for Docker builds & runtime)"
  type        = string
  default     = "t3.small"
}

variable "key_name" {
  description = "Optional SSH key pair name for EC2 access (leave empty when using SSM Session Manager)"
  type        = string
  default     = ""
}

variable "root_volume_size" {
  description = "Root GP3 EBS volume size in GB for the Docker host"
  type        = number
  default     = 20
}

# Database / RDS Variables
variable "db_instance_class" {
  description = "RDS DB instance class for PostgreSQL (db.t4g.micro is Graviton2 powered, cost-optimized for development/demos)"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage size in GB for the RDS PostgreSQL instance"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "Name of the default database to create on RDS PostgreSQL"
  type        = string
  default     = "cloudmodx_db"
}

variable "db_username" {
  description = "Master username for the RDS PostgreSQL instance"
  type        = string
  default     = "cloudmodx_user"
}

variable "db_password" {
  description = "Master password for the RDS PostgreSQL instance (must be at least 8 characters, securely passed in production)"
  type        = string
  sensitive   = true
  default     = "CloudModX_Secure_2026!"
}

variable "db_backup_retention_period" {
  description = "Backup retention period in days (0 disables automated backups for temporary demo)"
  type        = number
  default     = 0
}
