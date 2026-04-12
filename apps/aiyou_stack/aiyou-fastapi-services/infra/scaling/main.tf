terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" { type = string }
variable "region"     { type = string }

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Instance Template (The Swarm Unit)
resource "google_compute_instance_template" "monkey_template" {
  name_prefix  = "n-autoresearch/Kosmos/BioAgents-tpl-"
  machine_type = "e2-standard-4"
  region       = var.region

  disk {
    source_image = "cos-cloud/cos-stable"
    auto_delete  = true
    boot         = true
  }

  network_interface {
    network    = "default"
    subnetwork = "default"
  }

  metadata_startup_script = <<SCRIPT
    #! /bin/bash
    echo "Starting n-autoresearch/Kosmos/BioAgentss Server..."
    docker run -d -p 8600:8600 gcr.io/${var.project_id}/n-autoresearch/Kosmos/BioAgentss:latest
  SCRIPT

    create_before_destroy = true
  }

  resource_policies = [google_compute_resource_policy.unified_maintenance.id]
}

# 1.5 Unified Maintenance Policy (Sundays 02:00 UTC)
resource "google_compute_resource_policy" "unified_maintenance" {
  name   = "antigravity-maintenance"
  region = var.region

  instance_schedule_policy {
    vm_start_schedule {
      schedule = "0 2 * * 0" # Start check (Maintenance Window Start)
    }
    vm_stop_schedule {
      schedule = "0 6 * * 0" # Stop check (Maintenance Window End - 4h window)
    }
    time_zone = "Etc/UTC"
  }
}

# 2. Managed Instance Group (The Swarm)
resource "google_compute_region_instance_group_manager" "monkey_swarm" {
  name               = "n-autoresearch/Kosmos/BioAgents-swarm"
  base_instance_name = "monkey"
  region            = var.region
  target_size       = 3

  version {
    instance_template = google_compute_instance_template.monkey_template.id
  }

  auto_healing_policies {
    health_check      = google_compute_health_check.monkey_health.id
    initial_delay_sec = 300
  }
}

# 3. Health Check
resource "google_compute_health_check" "monkey_health" {
  name = "monkey-health"

  http_health_check {
    port = 8600
    request_path = "/health"
  }
}

# 4. Load Balancer (The Gate)
resource "google_compute_region_backend_service" "monkey_backend" {
  name                  = "monkey-backend"
  region                = var.region
  load_balancing_scheme = "EXTERNAL"
  protocol              = "HTTP"

  backend {
    group = google_compute_region_instance_group_manager.monkey_swarm.instance_group
  }

  health_checks = [google_compute_health_check.monkey_health.id]
}
