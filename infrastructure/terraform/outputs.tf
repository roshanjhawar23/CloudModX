output "aws_region" {
  description = "The configured AWS region for CloudModX infrastructure"
  value       = var.aws_region
}

output "environment" {
  description = "The target deployment environment"
  value       = var.environment
}

output "project_name" {
  description = "The project name identifier"
  value       = var.project_name
}

output "artifact_bucket_name" {
  description = "The globally unique name of the S3 bucket for module artifacts"
  value       = aws_s3_bucket.artifacts.id
}

output "artifact_bucket_arn" {
  description = "The Amazon Resource Name (ARN) of the S3 bucket for module artifacts"
  value       = aws_s3_bucket.artifacts.arn
}

# Networking Outputs
output "vpc_id" {
  description = "The ID of the CloudModX VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "The primary CIDR block of the CloudModX VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs in the CloudModX VPC"
  value = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id
  ]
}

output "private_subnet_ids" {
  description = "List of private subnet IDs in the CloudModX VPC"
  value = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id
  ]
}

output "internet_gateway_id" {
  description = "The ID of the CloudModX Internet Gateway"
  value       = aws_internet_gateway.main.id
}

# Compute / EC2 Outputs
output "ec2_instance_id" {
  description = "The ID of the CloudModX EC2 application host"
  value       = aws_instance.app_server.id
}

output "ec2_public_ip" {
  description = "The public IPv4 address of the CloudModX EC2 instance"
  value       = aws_instance.app_server.public_ip
}

output "ec2_public_dns" {
  description = "The public DNS hostname of the CloudModX EC2 instance"
  value       = aws_instance.app_server.public_dns
}

output "ec2_security_group_id" {
  description = "The ID of the EC2 application security group"
  value       = aws_security_group.app_server.id
}

output "ec2_iam_role_arn" {
  description = "The ARN of the IAM role attached to the EC2 application host"
  value       = aws_iam_role.app_server.arn
}

# Database / RDS Outputs
output "rds_instance_id" {
  description = "The identifier of the RDS PostgreSQL instance"
  value       = aws_db_instance.postgres.id
}

output "rds_endpoint" {
  description = "The connection endpoint (host:port) of the RDS PostgreSQL instance"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_address" {
  description = "The hostname / DNS address of the RDS PostgreSQL instance"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "The database port of the RDS PostgreSQL instance"
  value       = aws_db_instance.postgres.port
}

output "rds_database_name" {
  description = "The name of the database configured on the RDS PostgreSQL instance"
  value       = aws_db_instance.postgres.db_name
}

output "rds_username" {
  description = "The master username for the RDS PostgreSQL database"
  value       = aws_db_instance.postgres.username
  sensitive   = true
}

output "rds_security_group_id" {
  description = "The ID of the RDS security group"
  value       = aws_security_group.rds.id
}

output "rds_db_subnet_group_id" {
  description = "The ID of the RDS DB Subnet Group"
  value       = aws_db_subnet_group.rds.id
}

# Monitoring Outputs
output "cloudwatch_log_group_name" {
  description = "The name of the CloudWatch Log Group for application logs"
  value       = aws_cloudwatch_log_group.app_logs.name
}

output "cloudwatch_log_group_arn" {
  description = "The ARN of the CloudWatch Log Group for application logs"
  value       = aws_cloudwatch_log_group.app_logs.arn
}
