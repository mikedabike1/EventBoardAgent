output "prod_database_url" {
  description = "PostgreSQL connection string for production (Neon main branch, default role/database)"
  value       = neon_project.eventboard.connection_uri
  sensitive   = true
}

output "qa_database_url" {
  description = "PostgreSQL connection string for QA (Neon qa branch)"
  # Construct from parts. Neon passwords are URL-safe; verify after first apply.
  value = "postgresql://${neon_role.qa.name}:${neon_role.qa.password}@${neon_endpoint.qa.host}/${neon_database.qa.name}?sslmode=require"

  sensitive = true
}

output "neon_project_id" {
  description = "Neon project ID (useful for importing resources or Neon CLI)"
  value       = neon_project.eventboard.id
}
