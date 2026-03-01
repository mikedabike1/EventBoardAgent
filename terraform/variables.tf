variable "neon_region" {
  description = "Neon region for the project. See https://neon.tech/docs/introduction/regions"
  type        = string
  default     = "aws-us-east-2"
}

variable "project_name" {
  description = "Display name for the Neon project"
  type        = string
  default     = "eventboard"
}
