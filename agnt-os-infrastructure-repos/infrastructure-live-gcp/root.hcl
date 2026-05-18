remote_state {
  backend = "gcs"
  config = {
    bucket = "tfstate-${local.project_id}"
    prefix = "${path_relative_to_include()}/tfstate"
  }
  generate = { path = "backend.tf"; if_exists = "overwrite_terragrunt" }
}
