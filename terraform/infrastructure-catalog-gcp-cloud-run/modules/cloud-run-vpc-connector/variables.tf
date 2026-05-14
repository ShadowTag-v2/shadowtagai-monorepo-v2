variable "project_id"    { type = string }
variable "region"        { type = string; default = "us-central1" }
variable "name"          { type = string }
variable "subnet_name"   { type = string }
variable "machine_type"  { type = string; default = "e2-micro" }
variable "min_instances" { type = number; default = 2 }
variable "max_instances" { type = number; default = 10 }
