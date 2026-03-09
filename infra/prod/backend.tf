terraform {
  required_version = ">= 1.6.0"

  backend "s3" {
    bucket         = "gilles-jobassistant-tfstate"
    key            = "jobassistant/terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "jobassistant-tflocks"
    encrypt        = true
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.17.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "4.1.0"
    }
  }
}