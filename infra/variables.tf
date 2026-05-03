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

variable "notification_email" {
  description = "Email al que se envían las notificaciones de nuevos mensajes"
  type        = string
  default     = "lopezga30@hotmail.com"
}

variable "sender_email" {
  description = "Email verificado en SES que se usa como remitente (From)"
  type        = string
  default     = "lopezga30@gmail.com"
}
