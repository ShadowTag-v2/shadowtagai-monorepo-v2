# ============================================================================
# PNKLN CORE STACK - GKE + FILE SEARCH INTEGRATION
# ============================================================================
# Purpose: Deploy GKE cluster with Vertex AI File Search API integration
# Architecture: Judge 6 Hybrid + RAG-based Policy Enforcement
# Target: 30 vertical-specific policy corpora
# ============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }

  # Backend configuration for state management
  backend "gcs" {
    bucket = "pnkln-terraform-state"
    prefix = "gke-file-search"
  }
}

# ============================================================================
# LOCALS - VERTICAL DEFINITIONS
# ============================================================================

locals {
  # 30 Verticals with regulatory requirements
  verticals = {
    defense = {
      regulations = ["ITAR", "CMMC", "NISPOM"]
      description = "Defense and aerospace sector compliance"
    }
    healthcare = {
      regulations = ["HIPAA", "FDA_21_CFR_Part_11", "HITECH"]
      description = "Healthcare and medical device compliance"
    }
    finance = {
      regulations = ["FINRA", "SOX", "GDPR", "PCI_DSS"]
      description = "Financial services and banking compliance"
    }
    insurance = {
      regulations = ["State_Insurance_Regs", "NAIC", "SOX"]
      description = "Insurance and underwriting compliance"
    }
    pharmaceuticals = {
      regulations = ["FDA_GxP", "EMA", "21_CFR_Part_11"]
      description = "Pharmaceutical manufacturing compliance"
    }
    biotechnology = {
      regulations = ["FDA", "CLIA", "CAP"]
      description = "Biotech and laboratory compliance"
    }
    energy = {
      regulations = ["NERC_CIP", "FERC", "EPA"]
      description = "Energy sector and utilities compliance"
    }
    telecommunications = {
      regulations = ["FCC", "CALEA", "CPNI"]
      description = "Telecom and communications compliance"
    }
    aviation = {
      regulations = ["FAA_Part_121", "EASA", "TSA"]
      description = "Aviation and aerospace compliance"
    }
    maritime = {
      regulations = ["IMO", "SOLAS", "MARPOL"]
      description = "Maritime and shipping compliance"
    }
    manufacturing = {
      regulations = ["ISO_9001", "OSHA", "EPA"]
      description = "Manufacturing and industrial compliance"
    }
    automotive = {
      regulations = ["IATF_16949", "ISO_26262", "NHTSA"]
      description = "Automotive industry compliance"
    }
    retail = {
      regulations = ["PCI_DSS", "CPSC", "FTC"]
      description = "Retail and e-commerce compliance"
    }
    education = {
      regulations = ["FERPA", "COPPA", "HIPAA"]
      description = "Educational institutions compliance"
    }
    government = {
      regulations = ["FedRAMP", "FISMA", "NIST_800_53"]
      description = "Government and public sector compliance"
    }
    legal = {
      regulations = ["ABA_Model_Rules", "State_Bar_Regs", "GDPR"]
      description = "Legal services compliance"
    }
    real_estate = {
      regulations = ["RESPA", "TILA", "Fair_Housing"]
      description = "Real estate and property compliance"
    }
    hospitality = {
      regulations = ["PCI_DSS", "ADA", "OSHA"]
      description = "Hospitality and tourism compliance"
    }
    media = {
      regulations = ["FCC", "COPPA", "DMCA"]
      description = "Media and entertainment compliance"
    }
    agriculture = {
      regulations = ["USDA", "EPA", "FDA"]
      description = "Agriculture and food safety compliance"
    }
    construction = {
      regulations = ["OSHA", "EPA", "Building_Codes"]
      description = "Construction and engineering compliance"
    }
    logistics = {
      regulations = ["DOT", "FMCSA", "TSA"]
      description = "Logistics and transportation compliance"
    }
    chemicals = {
      regulations = ["EPA", "OSHA", "REACH"]
      description = "Chemical manufacturing compliance"
    }
    mining = {
      regulations = ["MSHA", "EPA", "OSHA"]
      description = "Mining and extraction compliance"
    }
    technology = {
      regulations = ["GDPR", "CCPA", "SOC_2"]
      description = "Technology and SaaS compliance"
    }
    cybersecurity = {
      regulations = ["NIST_CSF", "ISO_27001", "SOC_2"]
      description = "Cybersecurity services compliance"
    }
    consulting = {
      regulations = ["SOC_2", "ISO_9001", "GDPR"]
      description = "Professional consulting compliance"
    }
    nonprofit = {
      regulations = ["IRS_501c3", "State_Charity_Regs", "GDPR"]
      description = "Nonprofit and charitable organizations"
    }
    gaming = {
      regulations = ["Gaming_Commission", "AML", "KYC"]
      description = "Gaming and gambling compliance"
    }
    cannabis = {
      regulations = ["State_Cannabis_Regs", "FinCEN", "IRS_280E"]
      description = "Cannabis industry compliance"
    }
  }

  # Common tags for all resources
  common_tags = {
    Project     = "pnkln-core-stack"
    ManagedBy   = "Terraform"
    Component   = "file-search-integration"
    Environment = var.environment
  }
}

# ============================================================================
# MODULES
# ============================================================================

# GKE Cluster Module
module "gke" {
  source = "./modules/gke"

  project_id          = var.project_id
  region              = var.region
  cluster_name        = var.cluster_name
  network_name        = var.network_name
  subnetwork_name     = var.subnetwork_name

  # Node pool configuration
  node_pool_config = var.node_pool_config

  # Workload Identity enabled
  enable_workload_identity = true

  # Hypercomputer optimization (if in us-central1)
  enable_hypercomputer = var.region == "us-central1"

  labels = local.common_tags
}

# Vertex AI Module
module "vertex_ai" {
  source = "./modules/vertex-ai"

  project_id = var.project_id
  region     = var.region

  # RAG corpus configuration per vertical
  verticals = local.verticals

  # Corpus settings
  chunk_size    = var.rag_chunk_size
  chunk_overlap = var.rag_chunk_overlap

  depends_on = [module.gke]
}

# GCS Buckets for Policy Corpus
module "gcs" {
  source = "./modules/gcs"

  project_id      = var.project_id
  region          = var.region
  verticals       = local.verticals
  bucket_prefix   = var.bucket_prefix

  # Lifecycle policies
  enable_versioning = var.enable_bucket_versioning
  lifecycle_rules   = var.bucket_lifecycle_rules

  labels = local.common_tags
}

# IAM and Service Accounts
module "iam" {
  source = "./modules/iam"

  project_id           = var.project_id
  cluster_name         = module.gke.cluster_name
  gke_service_account  = module.gke.service_account_email

  # Workload Identity bindings
  workload_identity_namespace = var.workload_identity_namespace
  kubernetes_sa_name          = var.kubernetes_sa_name

  # Corpus bucket access
  corpus_buckets = module.gcs.bucket_names

  depends_on = [module.gke, module.gcs]
}

# ============================================================================
# OUTPUTS
# ============================================================================

output "gke_cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = module.gke.cluster_endpoint
  sensitive   = true
}

output "gke_cluster_name" {
  description = "GKE cluster name"
  value       = module.gke.cluster_name
}

output "corpus_buckets" {
  description = "GCS buckets for policy corpus (by vertical)"
  value       = module.gcs.bucket_details
}

output "vertex_ai_region" {
  description = "Vertex AI region for File Search API"
  value       = var.region
}

output "service_account_email" {
  description = "Service account for GKE workloads"
  value       = module.gke.service_account_email
}

output "workload_identity_config" {
  description = "Workload Identity configuration details"
  value = {
    namespace          = var.workload_identity_namespace
    kubernetes_sa_name = var.kubernetes_sa_name
    gcp_sa_email      = module.gke.service_account_email
  }
}
