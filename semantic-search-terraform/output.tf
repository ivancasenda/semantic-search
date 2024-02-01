output "storage-name" {
  description = "Storage Bucket Name"
  value       = google_storage_bucket.storage.name
}

output "docker-repo-name" {
  description = "Artifact Registry Repository Name"
  value       = google_artifact_registry_repository.docker.repository_id
}

output "vpc-network" {
  description = "VPC Network"
  value       = google_compute_network.vpc-network.name
}

output "connector-name" {
  description = "VPC Connector for Cloud Run"
  value       = google_vpc_access_connector.conn.name
}

output "service-account" {
  description = "Service Account Email"
  value       = google_service_account.project_sa.email
}
