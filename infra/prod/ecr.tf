resource "aws_ecr_repository" "jobassistant" {
  name                 = "jobassistant-app"
  image_tag_mutability = "IMMUTABLE" # Prevents overwriting tags

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256" # Standard AWS encryption
  }
}

# This policy keeps your bill low by only keeping the 5 most recent images
resource "aws_ecr_lifecycle_policy" "jobassistant_policy" {
  repository = aws_ecr_repository.jobassistant.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 5 images"
      selection = {
        tagStatus     = "any"
        countType     = "imageCountMoreThan"
        countNumber   = 5
      }
      action = {
        type = "expire"
      }
    }]
  })
}