# ==========================================
# GITHUB ACTIONS CI/CD ROLES
# ==========================================

data "tls_certificate" "github" {
  url = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_openid_connect_provider" "github_actions" {
  client_id_list  = ["sts.amazonaws.com"]
  url             = "https://token.actions.githubusercontent.com"
  thumbprint_list = [data.tls_certificate.github.certificates[0].sha1_fingerprint]
}

data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    sid = "1"
    actions = [
      "sts:AssumeRoleWithWebIdentity"
    ]
    effect = "Allow"
    principals {
      identifiers = [aws_iam_openid_connect_provider.github_actions.arn]
      type        = "Federated"
    }
    condition {
      test     = "StringEquals"
      values   = ["sts.amazonaws.com"]
      variable = "token.actions.githubusercontent.com:aud"
    }
    condition {
      test     = "StringLike"
      values   = ["repo:gillesvm/jobassistant:ref:refs/heads/main", "repo:gillesvm/jobassistant:pull_request"]
      variable = "token.actions.githubusercontent.com:sub"
    }
  }
}

resource "aws_iam_role" "github_actions_terraform" {
  name               = "github_actions_terraform"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role.json
}

resource "aws_iam_role_policy_attachment" "admin" {
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  role       = aws_iam_role.github_actions_terraform.name
}

# ==========================================
# ECS CONTAINER ROLES
# ==========================================

data "aws_iam_policy_document" "jobassistant_ecs_task_policy" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# Task Role: Used by the application code itself
resource "aws_iam_role" "jobassistant_ecs_task_role" {
  name               = "${local.name_prefix}-ecs-task-role"
  assume_role_policy = data.aws_iam_policy_document.jobassistant_ecs_task_policy.json
}

# Execution Role: Used by the ECS Agent to pull images and secrets
resource "aws_iam_role" "jobassistant_ecs_task_execution_role" {
  name               = "${local.name_prefix}-ecs-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.jobassistant_ecs_task_policy.json
}

resource "aws_iam_role_policy_attachment" "jobassistant_ecs_task_execution_role_attach" {
  role       = aws_iam_role.jobassistant_ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Custom SSM policy for the Execution Role to get the app authentication credentials
data "aws_iam_policy_document" "jobassistant_ecs_task_execution_ssm_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameters"
    ]
    resources = [
      aws_ssm_parameter.app_username.arn,
      aws_ssm_parameter.app_password_hash.arn,
      aws_ssm_parameter.session_secret_key.arn
    ]
  }
}

resource "aws_iam_policy" "jobassistant_ecs_task_execution_ssm_policy" {
  name   = "${local.name_prefix}-ecs-task-execution-ssm-policy"
  policy = data.aws_iam_policy_document.jobassistant_ecs_task_execution_ssm_policy.json
}

resource "aws_iam_role_policy_attachment" "jobassistant_ecs_task_execution_ssm_policy_attach" {
  role       = aws_iam_role.jobassistant_ecs_task_execution_role.name
  policy_arn = aws_iam_policy.jobassistant_ecs_task_execution_ssm_policy.arn
}