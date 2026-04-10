# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

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