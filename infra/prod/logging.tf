resource "aws_cloudwatch_log_group" "jobassistant" {
  name              = "/${local.project}/${local.environment}/general"
  retention_in_days = 30
}