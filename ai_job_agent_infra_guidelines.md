# AI Job Search Automation -- Infrastructure Guidelines

These guidelines outline a **production‑style approach** to building a
personal job‑search automation system using **Terraform, AWS, and GitHub
Actions**.\
The goal is to learn real infrastructure patterns while building
something useful.

This document focuses on **principles and sequencing**, not step‑by‑step
code.

------------------------------------------------------------------------

# Guiding Principles

## 1. Separate Bootstrap Infrastructure from Workloads

Always split infrastructure into two layers.

### Bootstrap stack

Resources required **before Terraform can use remote state**:

-   S3 bucket for Terraform state
-   DynamoDB table for state locking
-   (optional) KMS key
-   GitHub OIDC provider
-   CI/CD IAM roles

### Workload stack

Resources used by your application:

-   Lambda functions
-   Step Functions
-   DynamoDB job tracker
-   S3 document storage
-   SES notifications
-   EventBridge schedules

Reason: avoids circular dependencies and mirrors real production
environments.

------------------------------------------------------------------------

## 2. One Environment Does Not Mean One State File

Even if you only run **one environment ("prod")**, split Terraform state
logically.

Example structure:

    state/prod/security.tfstate
    state/prod/core.tfstate
    state/prod/app.tfstate

Purpose:

-   isolate failure domains
-   reduce blast radius
-   simulate real enterprise setups

Typical breakdown:

  State      Contents
  ---------- -------------------------------------
  security   OIDC provider, CI/CD roles, KMS
  core       shared S3 buckets, DynamoDB tracker
  app        Lambdas, Step Functions, schedules

------------------------------------------------------------------------

## 3. CI/CD Should Prove Safety

Your pipeline should **validate infrastructure before deploying it**.

Minimum checks:

-   terraform fmt -check
-   terraform validate
-   terraform plan

Deployment should:

-   run automatically on `main`
-   require **manual approval**
-   use **environment protection** in GitHub

This mirrors real production change management.

------------------------------------------------------------------------

## 4. Never Use Long‑Lived AWS Credentials

Use **OIDC federation between GitHub and AWS**.

Workflow:

    GitHub Actions
        ↓
    OIDC token
        ↓
    AWS STS AssumeRoleWithWebIdentity
        ↓
    temporary credentials

Advantages:

-   no static secrets
-   short‑lived credentials
-   secure CI/CD integration

Restrict IAM trust policies to:

-   your repository
-   specific branches
-   optionally specific environments

------------------------------------------------------------------------

## 5. Move Fast First, Then Tighten Security

Early development should prioritize **progress over perfection**.

Common workflow:

1.  Start with broader IAM permissions
2.  Deploy the full system successfully
3.  Analyze required permissions
4.  Replace broad permissions with least privilege policies

Avoid spending days perfecting IAM before your system works.

------------------------------------------------------------------------

# Suggested Build Sequence

## Stage A -- Remote State Foundation

Goal: create reliable Terraform state management.

Resources:

-   S3 state bucket
-   DynamoDB lock table
-   bucket versioning
-   bucket encryption
-   public access blocking

Optional enhancements:

-   bucket access logging
-   lifecycle policies

Exit criteria:

-   Terraform runs successfully from a clean environment
-   state files appear in the S3 bucket
-   state locking works correctly

------------------------------------------------------------------------

## Stage B -- CI/CD Identity and Pipeline

Goal: deploy infrastructure securely from GitHub.

Infrastructure:

-   GitHub OIDC provider in AWS
-   Terraform deploy IAM role
-   GitHub Actions workflow

Pipeline behaviour:

### Pull Requests

    terraform fmt
    terraform validate
    terraform plan

### Main Branch

    terraform apply

Apply should require **manual approval** via GitHub environments.

Exit criteria:

-   PRs generate Terraform plans
-   merges trigger apply after approval

------------------------------------------------------------------------

## Stage C -- Core Shared Infrastructure

Goal: build stable primitives first.

Recommended resources:

### DynamoDB job tracker

Tracks:

-   discovered jobs
-   application status
-   interview stages
-   follow‑ups

Design considerations:

-   flexible schema
-   idempotent writes
-   optional TTL for temporary data

### S3 document storage

Stores:

-   job descriptions
-   generated resumes
-   cover letters
-   application notes

Enable:

-   versioning
-   encryption
-   public access blocking

### Logging

Explicitly define log retention for:

-   Lambda logs
-   Step Function logs

Exit criteria:

-   jobs and documents can be stored and retrieved
-   logs are retained with controlled lifecycle

------------------------------------------------------------------------

## Stage D -- Deploy a Minimal Lambda

Goal: learn the deployment pipeline.

Lambda should:

-   log structured events
-   write a test record to DynamoDB
-   read configuration from environment variables

Infrastructure:

-   Lambda execution role
-   CloudWatch log group
-   DynamoDB write permissions

Exit criteria:

-   Lambda deploys through CI/CD
-   invocation writes a record to DynamoDB
-   logs appear in CloudWatch

------------------------------------------------------------------------

## Stage E -- Workflow Orchestration

Goal: coordinate tasks reliably.

Components:

-   Step Functions state machine
-   EventBridge scheduled trigger

Start simple:

    EventBridge → StepFunction → Lambda

Enhancements later:

-   retries
-   failure handling
-   DLQ patterns

Exit criteria:

-   scheduled executions trigger workflows reliably

------------------------------------------------------------------------

## Stage F -- Job Ingestion

Goal: populate your job database safely.

Start with stable sources:

-   RSS feeds
-   official job APIs
-   curated company career pages

Avoid aggressive scraping early.

Normalize job records:

-   URL
-   company
-   title
-   location
-   timestamp
-   raw description

Store:

-   metadata → DynamoDB
-   raw description → S3

Critical rule:

**Ensure idempotency**.

A job ingestion run should never create duplicates.

Exit criteria:

-   repeated ingestion runs produce consistent results

------------------------------------------------------------------------

## Stage G -- AI Scoring and Drafting

Goal: accelerate applications while maintaining accuracy.

Create a **resume facts bank** containing:

-   verified experience
-   skills
-   achievements
-   projects

The AI must only use information from this dataset.

Pipeline:

    Job Description
          ↓
    Match scoring
          ↓
    Resume tailoring suggestions
          ↓
    Cover letter draft

Never allow the model to invent experience.

Human review should remain mandatory.

Exit criteria:

-   generated drafts are accurate
-   application preparation time decreases

------------------------------------------------------------------------

## Stage H -- Hardening and Observability

Goal: transform the system into a portfolio‑quality project.

Recommended improvements:

### Security

-   replace broad IAM policies
-   scope permissions to specific resources

### Monitoring

-   CloudWatch alarms for workflow failures
-   Step Function error alerts

### Cost Controls

-   AWS budget alerts
-   log retention limits
-   lifecycle policies

### Reliability

-   enforce idempotency across workflows
-   add retry logic where appropriate

Exit criteria:

-   system failures are observable
-   costs remain predictable
-   IAM follows least privilege principles

------------------------------------------------------------------------

# Production Patterns Worth Practicing

Implementing these patterns will make the project resemble real
infrastructure work:

-   state isolation
-   explicit log retention
-   idempotent workflows
-   approval‑gated deployments
-   short‑lived credentials
-   consistent tagging across resources

Suggested tag set:

    Environment = prod
    Owner       = personal
    Project     = job-agent
    ManagedBy   = terraform
    Repository  = github

------------------------------------------------------------------------

# Anti‑Patterns to Avoid

Avoid the following early on:

-   full browser automation for job applications
-   aggressive scraping of platforms like LinkedIn
-   excessive Terraform module abstraction too early
-   perfect IAM policies before functionality exists

Focus first on **working infrastructure**.

------------------------------------------------------------------------

# Strategic Perspective

This project should function as:

-   a **portfolio‑level infrastructure system**
-   a **personal productivity tool**
-   a **learning platform for production cloud patterns**

The most valuable capability is:

    discover → score → draft → track → remind

rather than fully automated job applications.

Human oversight remains critical.

------------------------------------------------------------------------

# Suggested First Milestone

If starting from scratch, the most valuable first milestone is:

**Remote state + CI/CD pipeline fully operational**.

This provides the foundation for everything that follows.
