output "dvc_remote_path" {
  description = "The path to the simulated DVC remote storage"
  value       = local_file.s3_bucket_simulation.filename
}

output "db_connection_info" {
  description = "Information about the simulated database"
  value       = local_file.rds_db_simulation.filename
}

output "api_cluster_info" {
  description = "Information about the simulated API cluster"
  value       = local_file.ecs_cluster_simulation.filename
}
