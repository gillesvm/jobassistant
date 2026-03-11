terraform {
  required_version = ">= 1.6.0"

  backend "s3" {
    bucket         = "gilles-jobassistant-tfstate"
    key            = "jobassistant/terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "jobassistant-tflocks"
    encrypt        = true
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.17.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "4.1.0"
    }
  }
}

resource "aws_s3_bucket" "artifact_bucket" {
  bucket = "gilles-jobassistant-artifacts"
}

resource "aws_s3_bucket_versioning" "versioning_artifact_bucket" {
  bucket = aws_s3_bucket.artifact_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "block_public_artifact_bucket" {
  bucket = aws_s3_bucket.artifact_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}