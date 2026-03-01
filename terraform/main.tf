# ── Neon Project ─────────────────────────────────────────────────────────────
#
# One project on the free tier. The project auto-creates:
#   • a "main" branch (prod)
#   • a default compute endpoint for the main branch
#   • a default database ("neondb") and role ("neondb_owner")
#
# The prod DATABASE_URL is taken directly from neon_project.eventboard.connection_uri.
resource "neon_project" "eventboard" {
  name      = var.project_name
  region_id = var.neon_region

  # Pin the Postgres major version so Neon upgrades don't break things silently.
  pg_version = 16

  # Scale compute to zero after 5 minutes of inactivity (free-tier friendly).
  branch {
    name = "main"
  }
}

# ── QA Branch ────────────────────────────────────────────────────────────────
#
# Branched from "main" so it starts with a copy of prod's schema.
# Gets its own compute endpoint and role/database so migrations can run
# independently without touching prod data.
resource "neon_branch" "qa" {
  project_id = neon_project.eventboard.id
  name       = "qa"
}

resource "neon_role" "qa" {
  project_id = neon_project.eventboard.id
  branch_id  = neon_branch.qa.id
  name       = "eventboard_app"
}

resource "neon_database" "qa" {
  project_id = neon_project.eventboard.id
  branch_id  = neon_branch.qa.id
  name       = "eventboard"
  owner_name = neon_role.qa.name
}

resource "neon_endpoint" "qa" {
  project_id = neon_project.eventboard.id
  branch_id  = neon_branch.qa.id
  type       = "read_write"
}
