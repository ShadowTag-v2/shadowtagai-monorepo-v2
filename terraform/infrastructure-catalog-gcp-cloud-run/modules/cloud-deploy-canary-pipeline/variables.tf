variable "project_id"             { type = string }
variable "region"                  { type = string; default = "us-central1" }
variable "name"                    { type = string }
variable "cloud_run_service_name"  { type = string }
variable "percentages"             { type = list(number); default = [25, 50, 75] }
variable "verify"                  { type = bool; default = true }
variable "description"             { type = string; default = "Automated canary pipeline for Cloud Run Gen2" }
