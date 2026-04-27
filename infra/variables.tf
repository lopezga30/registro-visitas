variable "aws_region" {
  description = "Región AWS"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nombre del proyecto (se usa como prefijo en todos los recursos)"
  type        = string
  default     = "registro-visitas"
}

variable "environment" {
  description = "Entorno: staging o production"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "El entorno debe ser staging o production."
  }
}
