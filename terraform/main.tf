terraform {
  required_version = ">= 1.0.0"
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.1"
    }
  }
}

provider "local" {}

# Simulate creating an S3 bucket for DVC remote storage
resource "local_file" "s3_bucket_simulation" {
  content  = "Simulated S3 Bucket for DVC Remote Storage. In a production environment, this would be an aws_s3_bucket resource."
  filename = "${path.module}/mock_infrastructure/dvc_remote_s3.txt"
}

# Simulate creating a Postgres Database for MLflow Tracking Server
resource "local_file" "rds_db_simulation" {
  content  = "Simulated RDS Postgres Database. Connection string: postgresql://${var.db_username}:${var.db_password}@mock-db-host:5432/mlflow"
  filename = "${path.module}/mock_infrastructure/mlflow_db.txt"
}

# Simulate an ECS Cluster / Kubernetes Cluster for the Flask API and React Frontend
resource "local_file" "ecs_cluster_simulation" {
  content  = "Simulated ECS Cluster for AQI Prediction API. Container images will be pulled from ECR and run here."
  filename = "${path.module}/mock_infrastructure/ecs_cluster.txt"
}
