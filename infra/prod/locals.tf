locals {
  project     = "jobassistant"
  environment = "prod"

  name_prefix = "${local.project}-${local.environment}"

  common_tags = {
    Project     = local.project
    Environment = local.environment
    ManagedBy   = "opentofu"
  }
}
