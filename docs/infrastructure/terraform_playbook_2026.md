# Comprehensive Terraform Playbook 2026
**Architecture:** Sovereign OS V8 / Alpha-Omega Thread
**Target Environment:** GCP (`shadowtag-omega-v4`)

## Executive Summary
This playbook dictates the orchestration of the 188 foundational blueprints stored in the `apps/external_sdks` cache. It defines the Zero-ETL embedding pipelines, the Serverless Cloud Run tri-nodes, and the VPC Service Controls necessary for the Dark Luxury commercial node.

## Phase 1: Core Networking & Identity
Before attempting deployment of the Judge 6.1 container, establish the `shadowtag-core-run-sa` identity and bind it to the proper Cloud SQL and BigQuery IAM roles.

```hcl
resource "google_service_account" "cloud_run_sa" {
  account_id   = "shadowtag-core-run-sa"
  display_name = "ShadowTag Core Cloud Run SA"
}

resource "google_project_iam_member" "bigquery_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}
```

## Phase 2: The Severless Swarm (Knative)
The Judge 6.1 Sentinel must be deployed with `minScale: 0` to preserve the Sovereign economic model.

```hcl
resource "google_cloud_run_v2_service" "judge_6_1_sentinel" {
  name     = "shadowtag-judge-6-1"
  location = "us-central1"
  ingress  = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    containers {
      image = "gcr.io/shadowtag-omega-v4/sentinel:latest"
      env {
        name  = "PERSONA_MODE"
        value = "judge_6_1"
      }
    }
    service_account = google_service_account.cloud_run_sa.email
  }
}
```

## Phase 3: Zero-ETL Database Linking
The BigQuery ML embedding logic depends on successful linkage with AlloyDB Omni. Refer to `.agent/docs/alloydb_omni_setup.md` for the proxy configuration.
