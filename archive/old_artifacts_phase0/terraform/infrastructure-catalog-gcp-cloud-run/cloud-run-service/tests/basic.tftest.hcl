# Terraform native test for cloud-run-service module
# Run with: terraform test
# See: https://developer.hashicorp.com/terraform/language/tests

variables {
  project_id   = "test-project-id"
  region       = "us-central1"
  service_name = "test-service"
  image        = "gcr.io/cloudrun/hello:latest"
  min_instances = 0
  max_instances = 5
  cpu          = "1000m"
  memory       = "256Mi"
  concurrency  = 80
  env          = "test"
}

run "validate_service_name_format" {
  command = plan

  # Valid name should pass planning
  assert {
    condition     = google_cloud_run_v2_service.main.name == "test-service"
    error_message = "Service name should match input variable."
  }
}

run "validate_gen2_execution_environment" {
  command = plan

  assert {
    condition     = google_cloud_run_v2_service.main.template[0].execution_environment == "EXECUTION_ENVIRONMENT_GEN2"
    error_message = "Must use Gen2 execution environment."
  }
}

run "validate_scaling_bounds" {
  command = plan

  assert {
    condition     = google_cloud_run_v2_service.main.template[0].scaling[0].min_instance_count == 0
    error_message = "min_instances should be 0."
  }

  assert {
    condition     = google_cloud_run_v2_service.main.template[0].scaling[0].max_instance_count == 5
    error_message = "max_instances should be 5."
  }
}

run "validate_labels" {
  command = plan

  assert {
    condition     = google_cloud_run_v2_service.main.labels["managed_by"] == "opentofu"
    error_message = "Must have managed_by=opentofu label."
  }

  assert {
    condition     = google_cloud_run_v2_service.main.labels["environment"] == "test"
    error_message = "Must have correct environment label."
  }
}

run "reject_invalid_service_name" {
  command = plan

  variables {
    service_name = "INVALID_NAME"
  }

  expect_failures = [
    var.service_name,
  ]
}

run "reject_negative_min_instances" {
  command = plan

  variables {
    min_instances = -1
  }

  expect_failures = [
    var.min_instances,
  ]
}
