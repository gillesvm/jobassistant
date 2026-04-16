resource "aws_ssm_parameter" "app_username" {
  name  = "/jobassistant/prod/APP_USERNAME"
  type  = "String"
  value = "changeme"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "app_password_hash" {
  name  = "/jobassistant/prod/APP_PASSWORD_HASH"
  type  = "SecureString"
  value = "changeme"

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "session_secret_key" {
  name  = "/jobassistant/prod/SESSION_SECRET_KEY"
  type  = "SecureString"
  value = "changeme"

  lifecycle {
    ignore_changes = [value]
  }
}
