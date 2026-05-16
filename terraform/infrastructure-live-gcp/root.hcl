locals {
  account_vars = read_terragrunt_config(find_in_parent_folders("account.hcl"))
  region_vars  = read_terragrunt_config(find_in_parent_folders("region.hcl"))
  account_name = local.account_vars.locals.account_name
  gcp_project  = local.account_vars.locals.gcp_project
  gcp_region   = local.region_vars.locals.gcp_region
}

remote_state {
  backend = "gcs"
  config = {
    bucket = "${get_env("TG_BUCKET_PREFIX", "tfstate-")}${local.account_name}-${local.gcp_region}"
    prefix = "${path_relative_to_include()}/tfstate"
  }
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<-EOF
    provider "google" {
      project = "${local.gcp_project}"
      region  = "${local.gcp_region}"
      default_tags {
        labels = {
          managed_by  = "terragrunt"
          environment = "${local.account_name}"
          repo        = "ShadowTag-v2/Monorepo-Uphillsnowball"
        }
      }
    }
  EOF
}

generate "versions" {
  path      = "versions.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<-EOF
    terraform {
      required_version = ">= 1.9.0"
      required_providers {
        google = {
          source  = "hashicorp/google"
          version = "~> 6.0"
        }
      }
    }
  EOF
}
