# CloudModX S3 Artifact Storage Bucket
# Dedicated storage for compiled modules, packages, and versioned artifacts.

resource "aws_s3_bucket" "artifacts" {
  bucket_prefix = "${var.artifact_bucket_prefix}-${var.environment}-"

  # Prevent accidental destruction of artifact storage
  force_destroy = false

  tags = {
    Name        = "${var.project_name}-Artifacts-${var.environment}"
    Purpose     = "ModuleArtifacts"
    Environment = var.environment
  }
}

# Ownership controls - Disable ACLs in favor of modern BucketOwnerEnforced
resource "aws_s3_bucket_ownership_controls" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Block all public access at the bucket level
resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning for module artifact lifecycle tracking and rollback
resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption configuration using SSE-S3 (AES256)
resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Lifecycle rule to clean up incomplete multipart uploads after 7 days
resource "aws_s3_bucket_lifecycle_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    id     = "cleanup-incomplete-multipart-uploads"
    status = "Enabled"

    filter {}

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}
