# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

## [1.3.2] - 2026-04-17

### Fixed

- Injected strictly scoped IAM permissions into `jobassistant_ecs_task_role` granting granular read/write capability to DynamoDB and S3 bucket resources preventing backend 500 configuration errors.
- Passed `DYNAMODB_TABLE_NAME`, `S3_BUCKET_NAME`, and `AWS_REGION` implicitly into the ECS `container_definitions` environment array mapping natively to OpenTofu dynamic resources.

## [1.3.1] - 2026-04-17

### Added

- Set the desired count of the ECS service to 1

## [1.3.0] - 2026-04-17

### Added

- Dockerized the application with an optimized `python:3.11-slim` Dockerfile
- Configured automated `.github/workflows/app-deploy.yml` CI/CD pipeline driven entirely by OpenTofu backend outputs
- Updated the app authentication to use bcrypt hashes instead of plain text
- Added `ssm.tf` to securely store app credentials in AWS SSM Parameter Store
- Injected SSM secrets into the ECS task definition in `ecs.tf`
- Added `ssm:GetParameters` statement to the ECS execution IAM policy
- Added `app_url` and `alb_dns_name` explicitly to OpenTofu `outputs.tf` for deployment visibility

## [1.2.2] - 2026-04-15

### Fixes

- Fixed the ECS task IAM policy attachment

## [1.2.1] - 2026-04-14

### Fixes
- Fixed ECS task and execution role trust policy by removing invalid `resources` field from assume role policy document

### Changed
- Added 30-minute timeout to `tofu-apply.yml` to prevent pipeline hanging on long-running resources

### Added
- Created a custom VPC architecture using public subnets for cost-efficient container hosting.
- Set up an ECR repository with automated image scanning and a 5-image lifecycle retention policy.
- Implemented a CI/CD guardrail to enforce CHANGELOG.md updates on all Pull Requests.
- Added security groups for VPC traffic
- Added ALB for public access to the application
- Added ACM and Route53 for custom domain and https
- Consolidated IAM resources and added ECS Fargate infrastructure with initial count 0

## [1.2.0] - 2026-04-10

### Added

- Added additional fields when creating a new job
- Added docs folder with ui-improvements-suggestions.md file
- Added enhanced status badges
- Added form label and ARIA attribute improvements
- Added keyboard navigation and focus indicators
- Added toast notifications for user feedback
- Added custom color system and CSS variables

### Security

- Hardened GitHub Actions by pinning third-party actions to SHA hashes
- Enforced S3 Public Access Block and Ownership Controls in Terraform

### Fixes

- Fixed date display in existing jobs
- Fixed dashboard to properly show overdue follow-ups
- Fixed color contrast issues

## [1.1.0] - 2026-03-30

### Added

- Added changelog

### Fixes

- Fixed dashboard to show only relevant follow-ups
- Fixed GitHub readme display
- Fixed date notations

## [1.0.0] - 2026-03-15

### Added

- Initial Release (Job tracking, DynamoDB, Terraform infrastructure)