data "aws_region" "current" {}

resource "aws_ecs_cluster" "jobassistant_ecs" {
  name = "${local.name_prefix}-cluster"
}

resource "aws_ecs_task_definition" "jobassistant_task_definition" {
  family                   = "${local.name_prefix}-task-definition"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.jobassistant_ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.jobassistant_ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "${local.name_prefix}-container"
      image = "${aws_ecr_repository.jobassistant.repository_url}:latest"
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "DYNAMODB_TABLE_NAME"
          value = aws_dynamodb_table.jobassistant_jobs.name
        },
        {
          name  = "S3_BUCKET_NAME"
          value = aws_s3_bucket.job_artifacts.bucket
        },
        {
          name  = "AWS_REGION"
          value = data.aws_region.current.name
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.jobassistant.name
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = "ecs"
        }
      }
      secrets = [
        {
          name      = "APP_USERNAME"
          valueFrom = aws_ssm_parameter.app_username.arn
        },
        {
          name      = "APP_PASSWORD_HASH"
          valueFrom = aws_ssm_parameter.app_password_hash.arn
        },
        {
          name      = "SESSION_SECRET_KEY"
          valueFrom = aws_ssm_parameter.session_secret_key.arn
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "jobassistant_service" {
  name            = "${local.name_prefix}-service"
  cluster         = aws_ecs_cluster.jobassistant_ecs.id
  task_definition = aws_ecs_task_definition.jobassistant_task_definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    security_groups  = [aws_security_group.jobassistant_ecs_sg.id]
    subnets          = [aws_subnet.public_jobassistant_a.id, aws_subnet.public_jobassistant_b.id]
    assign_public_ip = true
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.jobassistant_tg.arn
    container_name   = "${local.name_prefix}-container"
    container_port   = 8000
  }

  lifecycle {
    ignore_changes = [task_definition]
  }
}

