variable "profile" {
  default     = "personal"
  description = "AWS SSO profile"
  type        = string
}

variable "environment" {
  description = "The environment abbreviation used in the naming scheme of many objects"
  type        = string
}

variable "region" {
  default     = "us-west-1"
  description = "AWS Deployment Region"
  type        = string
}
