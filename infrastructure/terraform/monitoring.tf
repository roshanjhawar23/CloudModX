# CloudModX Observability & Monitoring Infrastructure
# Provides lightweight, cost-conscious CloudWatch monitoring, alarms, and logging.

# 1. CloudWatch Log Group for Application & System Logs (7-day retention to minimize cost)
resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/cloudmodx/${var.environment}/application"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-App-Logs-${var.environment}"
  }
}

# 2. Attach CloudWatch Agent Policy to EC2 IAM Role for metric and log publishing
resource "aws_iam_role_policy_attachment" "cloudwatch_agent" {
  role       = aws_iam_role.app_server.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# 3. EC2 Metric Alarm: High CPU Utilization (> 80% for 10 minutes)
resource "aws_cloudwatch_metric_alarm" "ec2_high_cpu" {
  alarm_name          = "${var.project_name}-EC2-HighCPU-${var.environment}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Alarm triggers when EC2 CPU utilization exceeds 80% for 10 consecutive minutes."
  treat_missing_data  = "notBreaching"

  dimensions = {
    InstanceId = aws_instance.app_server.id
  }

  tags = {
    Name = "${var.project_name}-EC2-HighCPU-Alarm"
  }
}

# 4. EC2 Metric Alarm: System / Instance Status Check Failure
resource "aws_cloudwatch_metric_alarm" "ec2_status_check_failed" {
  alarm_name          = "${var.project_name}-EC2-StatusCheckFailed-${var.environment}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Maximum"
  threshold           = 1
  alarm_description   = "Alarm triggers when EC2 instance or system status checks fail."
  treat_missing_data  = "breaching"

  dimensions = {
    InstanceId = aws_instance.app_server.id
  }

  tags = {
    Name = "${var.project_name}-EC2-StatusCheck-Alarm"
  }
}

# 5. RDS Metric Alarm: High CPU Utilization (> 80% for 10 minutes)
resource "aws_cloudwatch_metric_alarm" "rds_high_cpu" {
  alarm_name          = "${var.project_name}-RDS-HighCPU-${var.environment}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Alarm triggers when RDS PostgreSQL CPU utilization exceeds 80% for 10 consecutive minutes."
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgres.identifier
  }

  tags = {
    Name = "${var.project_name}-RDS-HighCPU-Alarm"
  }
}

# 6. RDS Metric Alarm: Low Free Storage Space (< 2 GB remaining)
resource "aws_cloudwatch_metric_alarm" "rds_low_storage" {
  alarm_name          = "${var.project_name}-RDS-LowFreeStorage-${var.environment}"
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 2147483648 # 2 GB in bytes
  alarm_description   = "Alarm triggers when RDS PostgreSQL free storage space falls below 2 GB."
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgres.identifier
  }

  tags = {
    Name = "${var.project_name}-RDS-LowStorage-Alarm"
  }
}

# 7. RDS Metric Alarm: High Database Connections (> 40 connections)
resource "aws_cloudwatch_metric_alarm" "rds_high_connections" {
  alarm_name          = "${var.project_name}-RDS-HighConnections-${var.environment}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 40
  alarm_description   = "Alarm triggers when RDS PostgreSQL active connections exceed 40."
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgres.identifier
  }

  tags = {
    Name = "${var.project_name}-RDS-HighConnections-Alarm"
  }
}
