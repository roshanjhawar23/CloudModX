provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "CloudModX"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}
