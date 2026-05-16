terraform {
  backend "gcs" {
    bucket  = "shadowtag-omega-v4-tfstate"
    prefix  = "terraform/state"
  }
}
provider "google" {
  project = "shadowtag-omega-v4"
  region  = "us-central1"
}
