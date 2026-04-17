############################################
# outputs.tf
############################################

output "dynamodb_table_name" {
  value = aws_dynamodb_table.jobassistant_jobs.name
}

output "s3_bucket_name" {
  value = aws_s3_bucket.job_artifacts.bucket
}

output "ecr_repository_name" {
  value = aws_ecr_repository.jobassistant.name
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.jobassistant_ecs.name
}

output "ecs_service_name" {
  value = aws_ecs_service.jobassistant_service.name
}

output "ecs_task_family" {
  value = aws_ecs_task_definition.jobassistant_task_definition.family
}

output "ecs_container_name" {
  value = "${local.name_prefix}-container"
}

output "app_url" {
  value       = "https://${aws_route53_record.jobassistant_alias.name}"
  description = "The public URL of the application"
}

output "alb_dns_name" {
  value       = aws_lb.jobassistant_alb.dns_name
  description = "The raw DNS name of the Application Load Balancer"
}