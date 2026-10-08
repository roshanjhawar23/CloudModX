# CloudModX RDS PostgreSQL Database Infrastructure
# Provisions a secure, private, cost-conscious PostgreSQL RDS instance in isolated private subnets.

# 1. DB Subnet Group spanning Private Subnets A and B across 2 AZs
resource "aws_db_subnet_group" "rds" {
  name_prefix = "${lower(var.project_name)}-db-subnet-group-"
  description = "CloudModX DB subnet group in private subnets"
  subnet_ids = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id
  ]

  tags = {
    Name = "${var.project_name}-DB-Subnet-Group"
  }
}

# 2. Security Group for RDS PostgreSQL
resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds-sg-"
  description = "Security group for CloudModX RDS PostgreSQL instance (ingress strictly limited to EC2 App SG)"
  vpc_id      = aws_vpc.main.id

  # Allow inbound PostgreSQL (5432) ONLY from EC2 application security group
  ingress {
    description     = "PostgreSQL access from EC2 application host only"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app_server.id]
  }

  # Outbound egress
  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-RDS-SG"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# 3. RDS PostgreSQL Instance
resource "aws_db_instance" "postgres" {
  identifier_prefix = "${lower(var.project_name)}-db-"

  engine         = "postgres"
  engine_version = "15"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = 0 # Disables storage autoscaling to avoid unexpected costs
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible = false
  multi_az            = false

  backup_retention_period = var.db_backup_retention_period
  skip_final_snapshot     = true
  deletion_protection     = false
  apply_immediately       = true

  auto_minor_version_upgrade   = true
  allow_major_version_upgrade  = false
  performance_insights_enabled = false

  tags = {
    Name = "${var.project_name}-RDS-PostgreSQL"
    Role = "ProductionDatabase"
  }
}
