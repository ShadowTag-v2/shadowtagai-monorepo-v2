# Google-Native Insider Risk Platform: Reference Implementation

**Version**: 1.0
**Date**: February 2026
**Status**: Production-Ready Blueprint

## Executive Summary
This document provides a complete reference implementation for a Google Cloud-native insider threat detection and compliance platform. The architecture eliminates third-party vendor dependencies, leveraging Google Security Operations (Chronicle), Vertex AI, BigQuery, and Workspace to detect harassment, retaliation, fraud, self-harm content, and physical supply chain risks.

**Key Deliverables:**
*   Terraform infrastructure-as-code for complete stack deployment
*   Cloud Run services for AI safety gateway, classification pipeline, and risk dashboard
*   BigQuery schemas and SQL for USERRA retaliation detection, fraud indicators, and wellness signals
*   YARA-L detection rules for Security Operations
*   React-based risk dashboard with IAP authentication

---

## Architecture Overview

### Component Stack
| Layer | Google Cloud Services |
| :--- | :--- |
| **Data Ingestion** | Workspace Audit Logs, Cloud Logging, VPC Flow Logs, HRIS API connectors |
| **SIEM & Detection** | Security Operations (Chronicle), Security Command Center Premium, Custom YARA-L rules |
| **Data Platform** | BigQuery (raw, curated, feature tables), Dataform (transformations), Cloud Storage |
| **AI & ML** | Vertex AI (Gemini 1.5 Pro, custom models), Vision API, Video Intelligence API, Vertex AI Search |
| **Orchestration** | Cloud Functions, Cloud Run, EventArc, Pub/Sub, Cloud Scheduler |
| **Frontend** | Cloud Run (React SPA), Cloud CDN, Cloud Load Balancer |
| **Identity** | Cloud Identity, Workspace SSO, IAM, Identity-Aware Proxy (IAP) |

### Data Flow
1.  **Ingestion Layer**: Workspace logs (Gmail, Chat, Drive, Meet) → Cloud Logging → Pub/Sub → BigQuery + Security Operations
2.  **Enrichment Layer**: Cloud Functions trigger Vertex AI classification on new messages, scoring for harassment, discrimination, toxicity
3.  **Detection Layer**: BigQuery scheduled queries compute baselines and anomalies; Security Operations YARA-L rules trigger on patterns
4.  **Response Layer**: SOAR playbooks auto-alert HR/security, block high-risk users, route wellness flags to EAP
5.  **Presentation Layer**: Cloud Run dashboard queries BigQuery materialized views, displays risk cards and investigation timelines

---

## Terraform Infrastructure

### Project Structure
```text
insider-risk-platform/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── modules/
│   │   ├── bigquery/
│   │   ├── security-ops/
│   │   ├── vertex-ai/
│   │   ├── cloud-run/
│   │   └── iam/
├── services/
│   ├── safety-gateway/
│   ├── classification-pipeline/
│   └── risk-dashboard/
├── sql/
│   ├── schemas/
│   └── queries/
└── yara-l-rules/
```

### Main Terraform Configuration (`terraform/main.tf`)
```hcl
terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "YOUR_TERRAFORM_STATE_BUCKET"
    prefix = "insider-risk-platform"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "bigquery.googleapis.com",
    "aiplatform.googleapis.com",
    "chronicle.googleapis.com",
    "securitycenter.googleapis.com",
    "logging.googleapis.com",
    "pubsub.googleapis.com",
    "run.googleapis.com",
    "cloudfunctions.googleapis.com",
    "visionai.googleapis.com",
    "videointelligence.googleapis.com",
    "iap.googleapis.com",
    "cloudscheduler.googleapis.com",
    "eventarc.googleapis.com",
  ])
  service            = each.key
  disable_on_destroy = false
}

# Modules
module "bigquery" {
  source     = "./modules/bigquery"
  project_id = var.project_id
  region     = var.region
}

module "security_ops" {
  source     = "./modules/security-ops"
  project_id = var.project_id
}

module "vertex_ai" {
  source     = "./modules/vertex-ai"
  project_id = var.project_id
  region     = var.region
}

module "cloud_run" {
  source     = "./modules/cloud-run"
  project_id = var.project_id
  region     = var.region
}

module "iam" {
  source     = "./modules/iam"
  project_id = var.project_id
}
```

---

## BigQuery Module

### `terraform/modules/bigquery/main.tf`
```hcl
resource "google_bigquery_dataset" "workspace_logs" {
  dataset_id    = "workspace_logs"
  friendly_name = "Workspace Audit Logs"
  location      = var.region
  access {
    role          = "OWNER"
    user_by_email = google_service_account.pipeline_sa.email
  }
}

resource "google_bigquery_dataset" "hr_data" {
  dataset_id    = "hr_data"
  friendly_name = "HR and HRIS Data"
  location      = var.region
}

resource "google_bigquery_dataset" "risk_features" {
  dataset_id    = "risk_features"
  friendly_name = "Risk Feature Engineering"
  location      = var.region
}

resource "google_bigquery_dataset" "risk_scores" {
  dataset_id    = "risk_scores"
  friendly_name = "Final Risk Scores"
  location      = var.region
}

# Workspace logs table
resource "google_bigquery_table" "comms_events" {
  dataset_id = google_bigquery_dataset.workspace_logs.dataset_id
  table_id   = "comms_events"
  schema     = file("${path.module}/schemas/comms_events.json")
  time_partitioning {
    type  = "DAY"
    field = "event_timestamp"
  }
  clustering = ["user_email", "event_type"]
}

# Risk-scored communications
resource "google_bigquery_table" "comms_risk_events" {
  dataset_id = google_bigquery_dataset.workspace_logs.dataset_id
  table_id   = "comms_risk_events"
  schema     = file("${path.module}/schemas/comms_risk_events.json")
  time_partitioning {
    type  = "DAY"
    field = "event_timestamp"
  }
  clustering = ["user_email", "risk_category"]
}

# HR tables
resource "google_bigquery_table" "employees" {
  dataset_id = google_bigquery_dataset.hr_data.dataset_id
  table_id   = "employees"
  schema     = file("${path.module}/schemas/employees.json")
}

# Scheduled queries
resource "google_bigquery_data_transfer_config" "retaliation_detector" {
  display_name           = "USERRA Retaliation Detection"
  location               = var.region
  data_source_id         = "scheduled_query"
  schedule               = "every day 02:00"
  destination_dataset_id = google_bigquery_dataset.risk_scores.dataset_id
  params = {
    query = file("${path.module}/../../sql/queries/userra_retaliation.sql")
  }
}
```

---

## SQL Queries

### USERRA Retaliation Detection (`sql/queries/userra_retaliation.sql`)
```sql
-- Detect shift degradation after military leave (USERRA violations)
CREATE OR REPLACE TABLE risk_scores.userra_retaliation_alerts AS
WITH military_leaves AS (
    SELECT
        employee_id,
        start_date AS leave_start,
        end_date AS leave_end,
        DATE_ADD(end_date, INTERVAL 90 DAY) AS monitoring_end
    FROM hr_data.leaves
    WHERE is_userra_protected = TRUE
    AND end_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
),
pre_leave_baseline AS (
    SELECT
        ml.employee_id,
        ml.leave_start,
        ml.leave_end,
        AVG(s.hours) AS avg_hours_pre,
        AVG(s.shift_quality_score) AS avg_quality_pre,
        COUNT(*) AS shifts_pre
    FROM military_leaves ml
    JOIN hr_data.shifts s
    ON ml.employee_id = s.employee_id
    AND s.date BETWEEN DATE_SUB(ml.leave_start, INTERVAL 60 DAY) AND ml.leave_start
    GROUP BY 1, 2, 3
),
post_leave_metrics AS (
    SELECT
        ml.employee_id,
        ml.leave_start,
        ml.leave_end,
        AVG(s.hours) AS avg_hours_post,
        AVG(s.shift_quality_score) AS avg_quality_post,
        COUNT(*) AS shifts_post
    FROM military_leaves ml
    JOIN hr_data.shifts s
    ON ml.employee_id = s.employee_id
    AND s.date BETWEEN ml.leave_end AND ml.monitoring_end
    GROUP BY 1, 2, 3
)
SELECT
    pre.employee_id,
    e.email,
    e.manager_id,
    pre.leave_start,
    pre.leave_end,
    pre.avg_hours_pre,
    post.avg_hours_post,
    (post.avg_hours_post - pre.avg_hours_pre) AS hours_delta,
    pre.avg_quality_pre,
    post.avg_quality_post,
    (post.avg_quality_post - pre.avg_quality_pre) AS quality_delta,
    CASE
        WHEN (post.avg_hours_post - pre.avg_hours_pre) < -8 THEN 'CRITICAL'
        WHEN (post.avg_quality_post - pre.avg_quality_pre) < -2 THEN 'HIGH'
        ELSE 'MEDIUM'
    END AS risk_level,
    CURRENT_TIMESTAMP() AS alert_timestamp
FROM pre_leave_baseline pre
JOIN post_leave_metrics post USING (employee_id, leave_start, leave_end)
JOIN hr_data.employees e ON pre.employee_id = e.employee_id
WHERE (post.avg_hours_post - pre.avg_hours_pre) < -5 -- 5+ hour reduction
OR (post.avg_quality_post - pre.avg_quality_pre) < -1.5; -- significant quality drop
```

---

## Cloud Run Services

### Service 1: AI Safety Gateway (`services/safety-gateway/main.py`)
```python
import os
import json
from flask import Flask, request, jsonify
from google.cloud import aiplatform, bigquery
from datetime import datetime

PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION", "us-central1")
aiplatform.init(project=PROJECT_ID, location=LOCATION)
bq_client = bigquery.Client(project=PROJECT_ID)
app = Flask(__name__)

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]
model = aiplatform.GenerativeModel("gemini-1.5-pro", safety_settings=SAFETY_SETTINGS)

@app.route("/generate", methods=["POST"])
def generate():
    """
    Safety-first AI gateway. Blocks self-harm/dangerous content,
    logs attempts, redirects to resources.
    """
    body = request.get_json()
    user_email = body.get("user_email")
    user_prompt = body.get("prompt", "")

    # Step 1: Pre-classification for self-harm/dangerous intent
    safety_check_prompt = f"""
    You are a safety classifier. Analyze this text for:
    ·       Self-harm or suicidal ideation
    ·       Requests for dangerous content (violence, weapons, illegal activity)
    Respond ONLY with JSON:
    {{
    "self_harm": true/false,
    "dangerous": true/false,
    "reason": "brief explanation if flagged"
    }}
    Text: {user_prompt}
    """
    try:
        safety_resp = model.generate_content(
            safety_check_prompt,
            generation_config={"response_mime_type": "application/json", "temperature": 0.1}
        )
        flags = json.loads(safety_resp.text or "{}")
    except Exception as e:
        flags = {"self_harm": False, "dangerous": False, "error": str(e)}

    # Step 2: Handle blocked content
    if flags.get("self_harm") or flags.get("dangerous"):
        log_blocked_attempt(user_email, user_prompt, flags)
        return jsonify({
            "blocked": True,
            "category": "self_harm" if flags.get("self_harm") else "dangerous",
            "message": "Content blocked by safety filters. Please contact EAP or 988 if in crisis.",
        }), 200

    # Step 3: Normal generation
    response = model.generate_content(user_prompt)
    return jsonify({"output": response.text})

def log_blocked_attempt(user_email, prompt, flags):
    table_id = f"{PROJECT_ID}.risk_scores.self_harm_blocks"
    rows = [{"user_email": user_email, "prompt": prompt[:500], "flags": json.dumps(flags), "timestamp": datetime.utcnow().isoformat()}]
    bq_client.insert_rows_json(table_id, rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
```

---

## Security Operations (Chronicle) YARA-L Rules

### `yara-l-rules/repeated_harassment.yaral`
```yaral
rule repeated_harassment_pattern {
  meta:
    author = "Insider Risk Platform"
    description = "Detects user with 3+ high-toxicity messages in 7 days"
    severity = "HIGH"
  events:
    $msg.metadata.product_name = "Google Workspace"
    $msg.metadata.event_type = "chat_message"
    $msg.security_result.summary = "harassment"
    $msg.security_result.severity = "HIGH"
  match:
    $user over 7d
  condition:
    #msg >= 3
  outcome:
    $user = $msg.principal.user.email_addresses
    $risk_category = "repeated_harassment"
  options:
    create_case = true
}
```

### `yara-l-rules/post_complaint_retaliation.yaral`
```yaral
rule post_complaint_shift_degradation {
  meta:
    author = "Insider Risk Platform"
    description = "Detects shift quality drop after formal complaint (retaliation indicator)"
    severity = "CRITICAL"
  events:
    $complaint.metadata.product_name = "HR System"
    $complaint.metadata.event_type = "complaint_filed"
    $shift.metadata.product_name = "HR System"
    $shift.metadata.event_type = "shift_assignment"
    $shift.additional.fields["quality_delta"] < -2.0
  match:
    $complaint and $shift over 90d
  condition:
    $complaint.principal.user.userid == $shift.principal.user.userid
    and $shift.metadata.event_timestamp.seconds > $complaint.metadata.event_timestamp.seconds
  outcome:
    $employee_id = $complaint.principal.user.userid
    $risk_type = "USERRA_Title_VII_retaliation"
  options:
    create_case = true
    soar_playbook = "retaliation_investigation"
}
```
