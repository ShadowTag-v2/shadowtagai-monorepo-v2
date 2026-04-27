# Cloud Armor WAF Module (catalog version)
# Extracted from infra/cloud-armor/main.tf with parameterization

variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "service_name" {
  type        = string
  description = "Service name for policy naming."
}

variable "rate_limit_rpm" {
  type        = number
  default     = 100
  description = "Rate limit: requests per minute per IP."
}

variable "admin_rate_limit_rpm" {
  type        = number
  default     = 20
  description = "Admin endpoint rate limit: requests per minute per IP."
}

variable "admin_path_prefix" {
  type        = string
  default     = "/admin"
  description = "Path prefix for admin rate limiting."
}

variable "enable_xss" {
  type        = bool
  default     = true
  description = "Enable XSS protection rule."
}

variable "enable_sqli" {
  type        = bool
  default     = true
  description = "Enable SQL injection protection rule."
}

resource "google_compute_security_policy" "waf" {
  project = var.project_id
  name    = "${var.service_name}-waf"

  # XSS protection
  dynamic "rule" {
    for_each = var.enable_xss ? [1] : []
    content {
      action   = "deny(403)"
      priority = 1000
      match {
        expr {
          expression = "evaluatePreconfiguredExpr('xss-v33-stable')"
        }
      }
      description = "XSS protection"
    }
  }

  # SQLi protection
  dynamic "rule" {
    for_each = var.enable_sqli ? [1] : []
    content {
      action   = "deny(403)"
      priority = 1001
      match {
        expr {
          expression = "evaluatePreconfiguredExpr('sqli-v33-stable')"
        }
      }
      description = "SQL injection protection"
    }
  }

  # Admin rate limiting
  rule {
    action   = "throttle"
    priority = 1050
    match {
      expr {
        expression = "request.path.startsWith('${var.admin_path_prefix}')"
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      rate_limit_threshold {
        count        = var.admin_rate_limit_rpm
        interval_sec = 60
      }
    }
    description = "Admin rate limit ${var.admin_rate_limit_rpm} req/min/IP"
  }

  # General rate limiting
  rule {
    action   = "throttle"
    priority = 1100
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      rate_limit_threshold {
        count        = var.rate_limit_rpm
        interval_sec = 60
      }
    }
    description = "General rate limit ${var.rate_limit_rpm} req/min/IP"
  }

  # Default allow
  rule {
    action   = "allow"
    priority = 2147483647
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow"
  }

  lifecycle {
    prevent_destroy = true
  }
}

output "policy" {
  value       = google_compute_security_policy.waf
  description = "The Cloud Armor security policy resource."
}

output "policy_name" {
  value       = google_compute_security_policy.waf.name
  description = "Security policy name."
}

output "policy_self_link" {
  value       = google_compute_security_policy.waf.self_link
  description = "Security policy self_link for backend service attachment."
}
