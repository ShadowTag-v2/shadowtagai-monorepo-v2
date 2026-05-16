variable "project_id"   { type = string }
variable "region"       { type = string }
variable "service_name" { type = string }
variable "iam_bindings" {
  description = "Map of role => member (e.g. {\"roles/run.invoker\" = \"allUsers\"})."
  type        = map(string)
}
