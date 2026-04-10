locals {
  project     = "jobassistant"
  environment = "prod"
  domain      = "giftfinder.be"
  app_subdomain = "jobassistant"

  name_prefix = "${local.project}-${local.environment}" #tflint-ignore: terraform_unused_declarations

  common_tags = {
    Project     = local.project
    Environment = local.environment
    ManagedBy   = "opentofu"
  }
}
