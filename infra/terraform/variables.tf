variable "project_id" {
  description = "The GCP Project ID orchestrating the LawTrack infrastructure"
  type        = string
  default     = "shadowtag-omega-v4"
}

variable "region" {
  description = "Primary operating region"
  type        = string
  default     = "us-central1"
}
