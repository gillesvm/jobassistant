# JobAssistant AWS Deployment Analysis & Guide (Updated)

Based on a deeper analysis of the `jobassistant` repository, it's clear you already have a solid foundation:
* **Infrastructure**: OpenTofu (`infra/prod`) provisioning an S3 bucket (`job_artifacts`), a DynamoDB table (`job_tracker`), and an IAM OpenID Connect provider for GitHub Actions (`github_actions_terraform`).
* **CI/CD Pipelines**: GitHub Actions (`tofu-plan.yml` and `tofu-apply.yml`) that handle linting, planning, and applying OpenTofu code securely via OIDC.

To meet your requirements (cost-effective, custom domain, distributable, containerized) while building seamlessly on what you already have, here is the revised strategy.

---

## Deployment Strategy: ECS Fargate via OpenTofu

We will continue to use **Amazon ECS with Fargate**. This creates a highly reusable, containerized application that fits perfectly into your existing `infra/prod` OpenTofu state. By separating Application Code from Infrastructure Code within the same repository, we can leverage two distinct CI/CD pipelines.

### Infrastructure Expansion Requirements
Since you already have a `dynamodb.tf` and `s3.tf`, we will add the network and compute resources:
- **ECR Repository**: To store your Docker container images.
- **Network (VPC, Subnets)**: A standard VPC architecture to host containers securely.
- **Application Load Balancer (ALB) & ACM Certificate**: For routing HTTPS traffic from your Route 53 domain securely.
- **ECS Cluster & Fargate Service**: To run your container.

---

## Step-by-Step Guide

### Step 1: Expand OpenTofu Infrastructure
Add the container and networking infrastructure to the existing `infra/prod` directory.

1. **`ecr.tf`**: Create an AWS ECR repository (`jobassistant-app`).
2. **`vpc.tf`**: Provision a basic VPC with 2 public subnets (for ALB) and 2 private subnets (for Fargate tasks).
3. **`alb.tf` & `route53.tf`**: Provision an ALB, configure an ACM Certificate with DNS validation, and point your Route 53 subdomain alias (e.g., `app.yourdomain.com`) to the ALB. *The domain should be a new variable in `variables.tf`.*
4. **`ecs.tf`**: Create an ECS Cluster, Task Definition (pointing to the ECR image), and a Service. Map your existing IAM Roles so the container has access to your DynamoDB and S3 bucket without using secret keys.

### Step 2: Provision the Infrastructure
Since you already have `tofu-plan.yml` and `tofu-apply.yml` configured:
1. Create a Pull Request with the new `.tf` files.
2. The `tofu-plan.yml` pipeline will automatically run `tflint`, `checkov`, and upload a `tofu plan` to S3.
3. Upon merging to `main`, the `tofu-apply.yml` pipeline will execute the changes on AWS, bringing up the networking, ECR, and ECS service.

### Step 3: Containerize the Application
Add a `Dockerfile` to the root of your `app` directory.

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--forwarded-allow-ips", "*"]
```

### Step 4: Add an Application CI/CD Pipeline
Currently, your GitHub pipelines only handle OpenTofu. Add a new pipeline `.github/workflows/app-deploy.yml` that triggers specifically when changes occur in the `app/` folder.

This pipeline will:
1. Trigger on `push` to `main` modifying `app/**`.
2. Authenticate to AWS using your existing OIDC role.
3. Authenticate to ECR (`aws-actions/amazon-ecr-login`).
4. Build the Docker image with the Git commit hash as the tag and push it to your `jobassistant-app` ECR.
5. Update the ECS Service to force a new deployment with the latest image.

---

## Managing The App Lifecycle 

Once setup, here is how you and others will make changes to the app safely.

### 1. Modifying the Application (e.g. Updating Frontend, FastAPI logic)
* **How**: You change the Python code inside `app/` or HTML inside `app/templates/`.
* **Action**: Create a Pull Request, merge to `main`.
* **Pipeline Result**: The infrastructure CI/CD ignores this. The `app-deploy.yml` pipeline builds a new Docker Image, pushes it to ECR, and tells ECS to do a "rolling update". There is zero downtime, and AWS handles rotating out the old containers for the new ones.

### 2. Modifying the Infrastructure (e.g. Adding an SQS Queue, changing Domain)
* **How**: You change OpenTofu code inside `infra/prod/` (for instance, modifying `domain_name` in `.tfvars`).
* **Action**: Create a Pull Request, merge to `main`.
* **Pipeline Result**: The Application CI/CD ignores this. `tofu-plan.yml` runs safety checks, and upon merge, `tofu-apply.yml` updates the AWS infrastructure automatically.

By maintaining strict separation of concerns in your pipelines, your repository becomes highly distributable. Anyone can fork it, configure their GitHub Secrets and variables, and have a fully automated, containerized cloud application running on their own domain.
