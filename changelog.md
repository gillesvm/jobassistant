# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Added

- Updated the app authentication to use hashes instead of plain text
- Added ssm.tf to store secrets in AWS SSM Parameter Store for accessing the app
- Added the secrets to the ECS task definition in ecs.tf
- Added a statement to the ECS task IAM policy to allow access to the secrets in iam.tf

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