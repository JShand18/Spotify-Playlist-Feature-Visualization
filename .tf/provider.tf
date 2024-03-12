terraform {
  required_version = ">=1.2.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
}

# Configures AWS provider
provider "aws" {
  region = var.aws_region
  access_key = var.TF_VAR_ACCESS_KEY
  secret_key = var.TF_VAR_SECRET_KEY
}

