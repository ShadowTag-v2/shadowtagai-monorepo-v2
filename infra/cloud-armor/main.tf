# infra/cloud-armor/main.tf
# Cloud Armor WAF Management — OpenTofu/Terraform
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = "shadowtag-omega-v4"
  region  = "us-central1"
}

resource "google_compute_security_policy" "counselconduit_waf" {
  name = "counselconduit-waf"

  rule {
    action   = "rate_based_ban"
    priority = 900
    match {
      expr {
        expression = "request.path.matches('/admin/.*')"
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(403)"
      rate_limit_threshold {
        count        = 20
        interval_sec = 60
      }
      ban_duration_sec = 600
    }
    description = "Admin endpoints: 20 req/min per IP, 10min ban on exceed"
  }

  rule {
    action   = "deny(403)"
    priority = 950
    match {
      expr {
        expression = "request.query.lower().contains('ignore previous') || request.query.lower().contains('ignore all instructions') || request.query.lower().contains('system prompt') || request.path.lower().contains('..%2f') || request.path.lower().contains('%00')"
      }
    }
    description = "Block prompt injection patterns in URL params"
  }

  rule {
    action   = "deny(403)"
    priority = 1000
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-v33-stable')"
      }
    }
    description = "Block XSS attacks"
  }

  rule {
    action   = "deny(403)"
    priority = 1001
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('sqli-v33-stable')"
      }
    }
    description = "Block SQL injection"
  }

  rule {
    action   = "rate_based_ban"
    priority = 1100
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(403)"
      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }
      ban_duration_sec = 300
    }
    description = "Rate limit: 100 req/min per IP, 5min ban on exceed"
  }

  rule {
    action   = "allow"
    priority = 2147483647
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "default rule"
  }
}
