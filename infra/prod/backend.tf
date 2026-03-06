terraform {
  required_version = ">= 1.6.0"

  backend "s3" {
    bucket         = "gilles-jobassistant-tfstate"
    key            = "jobassistant/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "jobassistant-tflocks"
    encrypt        = true
  }
}