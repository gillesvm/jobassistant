resource "aws_dynamodb_table" "jobassistant_jobs" {
  name         = "${local.name_prefix}-job-tracker"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "job_id"
  range_key    = "item_type"

  attribute {
    name = "job_id"
    type = "S"
  }

  attribute {
    name = "item_type"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "S"
  }

  global_secondary_index {
    name            = "status-created-at-index"
    hash_key        = "status"
    range_key       = "created_at"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = local.common_tags
}