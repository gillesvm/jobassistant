############################################
# outputs.tf
############################################

output "dynamodb_table_name" {
  value = aws_dynamodb_table.jobassistant_jobs.name
}

output "s3_bucket_name" {
  value = aws_s3_bucket.job_artifacts.bucket
}