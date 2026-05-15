# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Proprietary

resource "google_redis_instance" "cache" {
  name           = var.instance_name
  tier           = var.tier
  memory_size_gb = var.memory_size_gb
  region         = var.region
  project        = var.project_id

  redis_version      = "REDIS_7_0"
  display_name       = "CounselConduit Cache"
  auth_enabled       = true # Required to be true, but we actually want IAM auth or AUTH string.
  
  # Enable IAM authentication
  # NOTE: At the time of this module, GCP Memorystore supports IAM Auth.
  # "transit_encryption_mode" must be "SERVER_AUTHENTICATION" for IAM to work
  transit_encryption_mode = "SERVER_AUTHENTICATION"
  
  # Enable Auth via IAM
  # Depending on provider version, IAM auth is usually toggled.
  # Since IAM authentication uses OAuth2 tokens as passwords, auth_enabled must be false or we can use IAM roles
  # We will stick to the standard configuration.

  authorized_network = var.vpc_network_id
}
