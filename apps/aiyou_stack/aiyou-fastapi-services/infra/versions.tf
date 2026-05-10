terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }

  # Backend configuration - uncomment and configure for production
  # backend "gcs" {
  #   bucket = "pnkln-terraform-state"
  #   prefix = "gke/prod"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Configure kubernetes provider after cluster creation
provider "kubernetes" {
  host                   = "https://${google_container_cluster.pnkln_cluster.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(google_container_cluster.pnkln_cluster.master_auth[0].cluster_ca_certificate)
}

data "google_client_config" "default" {}
