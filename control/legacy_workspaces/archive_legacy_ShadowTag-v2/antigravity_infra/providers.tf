terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "shadowtag-omega-v4"
  region  = "us-central1"
  zone    = "us-central1-a"
}

provider "google-beta" {
  project = "shadowtag-omega-v4"
  region  = "us-central1"
  zone    = "us-central1-a"
}
