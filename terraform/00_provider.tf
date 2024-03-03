provider "aws" {
  region = "us-west-2"
  profile = "personal"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.39.0"
    }
  }

  required_version = "~> 1.0"
}
