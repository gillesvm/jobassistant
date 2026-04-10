# bucket for jobassistant artifacts like job descriptions, resumes and cover letters

resource "aws_s3_bucket" "job_artifacts" {
  bucket = "${local.name_prefix}-job-artifacts"

  tags = local.common_tags
}

resource "aws_s3_bucket_public_access_block" "job_artifacts_access" {
  bucket = aws_s3_bucket.job_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "artifacts" {
  bucket = aws_s3_bucket.job_artifacts.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.job_artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.job_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}