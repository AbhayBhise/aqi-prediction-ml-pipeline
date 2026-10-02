variable "environment" {
  description = "The deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "db_username" {
  description = "Username for the simulated MLflow database"
  type        = string
  default     = "mlflow_user"
}

variable "db_password" {
  description = "Password for the simulated MLflow database"
  type        = string
  default     = "secure_password_123"
  sensitive   = true
}

variable "region" {
  description = "Simulated cloud region"
  type        = string
  default     = "ap-south-1"
}
