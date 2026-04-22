# JobAssistant

A web application to track and manage job applications, built as a DevOps learning project to practice AWS, OpenTofu (Terraform), Python, and CI/CD workflows.

## Project Evolution

The initial idea was to have AI assist with job matching and generating cover letters, but it felt better to first focus on building a solid tracker dashboard to properly manage applications. The AI features might be revisited once the core tracking functionality is solid and proving useful.

## Features

- **Job Application Tracking**: Track company, position, status, and follow-up dates.
- **Status Management**: Monitor applications through stages (new, applied, interviewing, rejected, etc.).
- **Smart Dashboard**: Visual overview with overdue follow-ups and upcoming tasks.
- **Rich Details**: Store job descriptions, resumes, cover letters, and interview notes.
- **Date Management**: Editable creation and follow-up dates for importing historical applications.
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
- **Custom VPC**: A scratch-built networking layer with public subnets across multiple Availability Zones for cost-efficient container hosting.
- **ALB & Route53**: Application Load Balancer safely exposing the application behind a custom Route53 HTTPS Domain.
- **S3 Security**: Hardened with Public Access Block, Ownership Controls, and AES-256 server-side encryption.
- **IAM Roles**: Least-privilege roles for GitHub Actions and application execution.

### Compute & Storage
- **ECS Fargate**: Fully Serverless Docker Container execution environment, securely integrated with AWS SSM tracking and CloudWatch logging.
- **DynamoDB**: Single-table design with Global Secondary Indexes (GSI) for efficient status-based queries.
- **ECR Repository**: Private container registry with `IMMUTABLE` tags, automated image scanning, and a lifecycle policy to retain the 5 most recent images.

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

## Local Setup

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
   Create a `.env` file in the `app/` directory and edit with your values:
   ```bash
   APP_USERNAME=your_username
   APP_PASSWORD=your_password
   SESSION_SECRET_KEY=your_secret_key_here
   DYNAMODB_TABLE_NAME=your-dynamodb-table-name
   S3_BUCKET_NAME=your-s3-bucket-name
   AWS_REGION=eu-central-1
   ```

5. **Deploy AWS infrastructure**
   ```bash
   cd infra/prod
   tofu init
   tofu plan
   tofu apply
   ```

6. **Run the application**
   ```bash
   cd app
   uvicorn main:app --reload
   ```

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

This is a personal learning project, but suggestions and feedback are welcome via issues!