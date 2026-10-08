# CloudModX EC2 Application Host Infrastructure
# Provisions a cost-effective EC2 instance in Public Subnet A with Docker pre-installed.

# Lookup latest Amazon Linux 2023 AMI (x86_64)
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

# 1. Security Group for Application Server
# SSH (Port 22) is removed; administrative access is provided securely via AWS Systems Manager (SSM).
# Only standard HTTP (Port 80) is publicly accessible; reverse-proxies /api/ to backend internally.
resource "aws_security_group" "app_server" {
  name_prefix = "${var.project_name}-app-sg-"
  description = "Security group for CloudModX application host (HTTP 80, temporary demo ports 3000/8000)"
  vpc_id      = aws_vpc.main.id

  # Standard Public HTTP
  ingress {
    description = "Standard HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound egress to anywhere (for OS updates, Docker Hub pulls, S3 API calls, RDS private access)
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-App-SG"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# 2. IAM Role & Instance Profile for EC2 (SSM Session Manager & S3 Artifact Access)
resource "aws_iam_role" "app_server" {
  name_prefix = "${var.project_name}-ec2-role-"
  description = "IAM Role for CloudModX EC2 application host"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-EC2-IAM-Role"
  }
}

# Attach AWS Systems Manager Managed Policy (Enables secure SSH-free terminal access via SSM)
resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.app_server.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Attach S3 Artifact Storage Access Policy (Explicitly scoped to the exact Terraform S3 bucket ARN)
resource "aws_iam_role_policy" "s3_artifacts_access" {
  name_prefix = "${var.project_name}-s3-access-"
  role        = aws_iam_role.app_server.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3BucketLevelAccess"
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          aws_s3_bucket.artifacts.arn
        ]
      },
      {
        Sid    = "S3ObjectLevelAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${aws_s3_bucket.artifacts.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_instance_profile" "app_server" {
  name_prefix = "${var.project_name}-ec2-profile-"
  role        = aws_iam_role.app_server.name

  tags = {
    Name = "${var.project_name}-EC2-Instance-Profile"
  }
}

# 3. EC2 Application Server Instance in Public Subnet A
resource "aws_instance" "app_server" {
  ami                         = data.aws_ami.al2023.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public_a.id
  vpc_security_group_ids      = [aws_security_group.app_server.id]
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.app_server.name
  key_name                    = var.key_name != "" ? var.key_name : null

  # Cost-conscious GP3 root volume
  root_block_device {
    volume_size           = var.root_volume_size
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-AppServer-RootVolume"
    }
  }

  # User Data Script to install Docker and Docker Compose
  user_data = <<-EOF
              #!/bin/bash
              set -euxo pipefail

              # Update system packages
              dnf update -y

              # Install Docker, Git, and utilities
              dnf install -y docker git libxcrypt-compat jq --allowerasing

              # Enable and start Docker service
              systemctl enable --now docker

              # Allow ec2-user to execute docker commands without sudo
              usermod -aG docker ec2-user

              # Install Docker Compose plugin (v2)
              DOCKER_CONFIG=/usr/local/lib/docker
              mkdir -p $DOCKER_CONFIG/cli-plugins
              COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | jq -r .tag_name || echo "v2.29.7")
              curl -sL "https://github.com/docker/compose/releases/download/$${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o $DOCKER_CONFIG/cli-plugins/docker-compose
              chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
              ln -sf $DOCKER_CONFIG/cli-plugins/docker-compose /usr/local/bin/docker-compose

              # Prepare app directory
              mkdir -p /opt/cloudmodx
              chown -R ec2-user:ec2-user /opt/cloudmodx

              echo "CloudModX Docker host bootstrap completed successfully."
              EOF

  tags = {
    Name = "${var.project_name}-AppServer-${var.environment}"
    Role = "ApplicationHost"
  }
}
