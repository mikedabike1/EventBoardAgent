terraform {
  required_version = ">= 1.5"

  required_providers {
    neon = {
      source  = "kislerdm/neon"
      version = "~> 0.6"
    }
  }

  # Terraform Cloud backend for remote state.
  # Set TF_CLOUD_ORGANIZATION and TF_WORKSPACE env vars, or fill in below.
  # Run: terraform init -backend-config=backend.hcl  (see backend.hcl.example)
  backend "remote" {
    # organization is read from TF_CLOUD_ORGANIZATION env var in CI,
    # or set it here for local use.
    organization = "YOUR_TF_CLOUD_ORG"

    workspaces {
      name = "eventboard"
    }
  }
}

# The Neon provider reads NEON_API_KEY from the environment.
# Set this as a secret in Terraform Cloud (or export it locally).
provider "neon" {}
