resource "aws_dynamodb_table" "jobassistant_dynamodb" {
  name = "${local.name_prefix}-job-tracker"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "hk"
  range_key = "rk"

  attribute {
    name = "hk"
    type = "S"
  }

  attribute {
    name = "rk"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = local.common_tags

}