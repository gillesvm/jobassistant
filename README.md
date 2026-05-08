# JobAssistant

A personal project to track job applications. During my search for a new job I found it difficult to properly track and
follow up on job applications. That is why I built this tool to better track the applications.
This project also serves as a technical sandbox for implementing AWS resources, Infrastructure as Code (OpenTofu), and
automated CI/CD
pipelines in Github.

## Project Evolution

The initial idea was to have AI assist with job matching and generating cover letters, but it felt better to first focus
on building a solid tracker dashboard to properly manage applications. The AI features might be revisited later once the
core
tracking functionality is solid and proving useful.

## Engineering Philosophy & Design Decisions

Instead of a standard CRUD app, I built this focusing on the AWS Well-Architected Framework:

- **Why DynamoDB (Single-Table Design)** I chose a NoSQL approach using GSI (Global Secondary Indexes) to practice
  high-performance modeling. It ensures the app remains snappy and cost-effective even as the application list grows,
  avoiding the overhead of relational joins for simple state transitions.
- **Why ECS Fargate?** I prioritized Operational Excellence. By using a serverless container move, I eliminated the
  burden of managing EC2 instances, focusing entirely on the application lifecycle.
- **Why OpenTofu?** Adopting the open-source fork of Terraform to maintain vendor-neutrality while leveraging modern IaC
  features like state locking and modularity.
- **Security First:** I implemented a Zero-Trust approach for the build pipeline. GitHub Actions communicates with AWS
  via OIDC (OpenID Connect), eliminating the need for long-lived IAM Secret Keys.

## Features

- **Job Application Tracking**: Track company, position, status, and follow-up dates.
- **Status Management**: Monitor applications through stages (new, applied, interviewing, rejected, etc.).
- **Smart Dashboard**: Visual overview with overdue follow-ups and upcoming tasks.
- **Rich Details**: Store job descriptions, resumes, cover letters, and interview notes.
- **Filtering**: Filter jobs by status for easy organization.

## Tech Stack

**Frontend:**

- FastAPI (Python web framework)
- Jinja2 templates
- Bootstrap 5

**Backend:**

- Python 3.13
- AWS DynamoDB (NoSQL database using single-table design)
- AWS S3 (Artifact storage for resumes/cover letters)

**Infrastructure:**

- OpenTofu / Terraform (Infrastructure as Code)
- AWS (DynamoDB, S3, VPC, ECR)
- GitHub Actions (CI/CD with automated validation and linting)

## AWS Infrastructure

The infrastructure follows a modular, secure-by-default design.

### Networking & Security

- **Custom VPC**: A scratch-built networking layer with public subnets across multiple Availability Zones for
  cost-efficient container hosting.
- **ALB & Route53**: Application Load Balancer safely exposing the application behind a custom Route53 HTTPS Domain.
- **S3 Security**: Hardened with Public Access Block, Ownership Controls, and AES-256 server-side encryption.
- **IAM Roles**: Least-privilege roles for GitHub Actions and application execution.

### Compute & Storage

- **ECS Fargate**: Fully Serverless Docker Container execution environment, securely integrated with AWS SSM tracking
  and CloudWatch logging.
- **DynamoDB**: Single-table design with Global Secondary Indexes (GSI) for efficient status-based queries.
- **ECR Repository**: Private container registry with `IMMUTABLE` tags, automated image scanning, and a lifecycle policy
  to retain the 5 most recent images.

## Project Structure

```text
jobassistant/
├── app/                  # Python web application
│   ├── routes/           # FastAPI route handlers
│   ├── services/         # Business logic (DynamoDB, S3)
│   └── templates/        # Jinja2 HTML templates
│   └── main.py           # FastAPI entry point
├── infra/                # Terraform/OpenTofu infrastructure
│   └── prod/             # Production environment configuration
├── docs/                 # Documentation and UI improvement suggestions
├── .github/              # GitHub Actions workflows
├── README.md
└── CHANGELOG.md
```

## Setup & Deployment

### Local Development

Local development requires connecting to the AWS infrastructure (DynamoDB and S3). Ensure you have valid AWS credentials configured.

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd jobassistant
   ```

2. **Create virtual environment**
   ```bash
   cd app
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the `app/` directory. **Note:** `APP_PASSWORD_HASH` must be a Bcrypt hash.
   ```bash
   APP_USERNAME=your_username
   APP_PASSWORD_HASH=your_bcrypt_hash_here  # Use a tool to generate a bcrypt hash
   SESSION_SECRET_KEY=your_secret_key_here
   DYNAMODB_TABLE_NAME=jobassistant-prod-jobs
   S3_BUCKET_NAME=your-s3-bucket-name
   AWS_REGION=eu-central-1
   ```

---

### AWS Deployment Guide

This project uses **GitHub Actions** for automated infrastructure updates and application deployments. However, a manual bootstrap is required for the initial "chicken and egg" resources.

#### 1. Prerequisites
- **Custom Domain:** You MUST have a custom domain managed via **AWS Route53**. Update `infra/prod/locals.tf` with your domain and subdomain.
- **AWS CLI & OpenTofu:** Ensure you have the AWS CLI configured with administrator permissions and OpenTofu installed locally.

#### 2. OIDC "Chicken & Egg" Setup (Manual)
To enable GitHub Actions to deploy without long-lived secrets, you must manually establish trust between GitHub and AWS. While the IaC contains these resources, you need them *before* the first automated run.

1. **Create Identity Provider:** In the AWS IAM Console, add an OpenID Connect provider:
   - **Provider URL:** `https://token.actions.githubusercontent.com`
   - **Audience:** `sts.amazonaws.com`
2. **Create IAM Role:** Create a role named `github_actions_terraform` with:
   - **Trust Policy:** Allow `AssumeRoleWithWebIdentity` from the OIDC provider.
   - **Condition:** `StringLike` on `token.actions.githubusercontent.com:sub` for `repo:<your-github-handle>/jobassistant:*`.
   - **Permissions:** Attach `AdministratorAccess`.
3. **GitHub Secrets:** Add the ARN of this role as a GitHub secret named `AWS_GITHUB_ACTIONS_ROLE_ARN`.

#### 3. Bootstrap ECR Repository
The ECS service cannot start without an initial image. First, deploy only the ECR repository locally:
```bash
cd infra/prod
tofu init
tofu apply -target=aws_ecr_repository.jobassistant
```

#### 4. Build and Push Initial Image
Login to ECR and push the first version of your application. This unblocks the ECS service creation in the pipeline.
```bash
# Get ECR login token
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.eu-central-1.amazonaws.com

# Build and tag (Run from root)
docker build -t jobassistant-app ./app
docker tag jobassistant-app:latest <aws_account_id>.dkr.ecr.eu-central-1.amazonaws.com/jobassistant-prod-app:latest

# Push
docker push <aws_account_id>.dkr.ecr.eu-central-1.amazonaws.com/jobassistant-prod-app:latest
```

#### 5. Automated Deployment (GitHub Actions)
Once the bootstrap is complete, all further updates should be handled via GitHub Actions:

- **Infrastructure Changes:** Trigger the `OpenTofu Apply` workflow manually via the "Actions" tab.
- **Application Updates:** Pushing changes to the `main` branch under the `app/` directory will automatically trigger the `App Build & Deploy` workflow.

Your application will be live at `https://jobassistant.yourdomain.com`.
## Future Enhancements

- [x] Create Custom VPC Infrastructure
- [x] Setup ECR Repository
- [x] Containerize with Docker
- [x] Deploy to AWS ECS (Fargate)
- [x] Custom domain with Route53
- [ ] AI-powered resume/cover letter generation

## License

MIT License - feel free to use this project for learning purposes.

## Contributing

This is a personal project, but suggestions and feedback are welcome via issues!