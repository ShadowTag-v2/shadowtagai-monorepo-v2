variable "project_id"            { type = string }
variable "service_account_email" { type = string }
variable "secret_ids" {
  description = "List of Secret Manager secret IDs to grant access to."
  type        = list(string)
}
