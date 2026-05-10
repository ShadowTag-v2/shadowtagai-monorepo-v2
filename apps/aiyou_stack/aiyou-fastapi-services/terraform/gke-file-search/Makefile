# ============================================================================
# MAKEFILE - PNKLN CORE STACK GKE + FILE SEARCH
# ============================================================================
# Convenient commands for managing Terraform deployment
# ============================================================================

.PHONY: help init plan apply destroy validate format clean status

# Default target
.DEFAULT_GOAL := help

# Variables
PROJECT_ID ?= pnkln-core-gke
REGION ?= us-central1
CLUSTER_NAME ?= pnkln-core-cluster

help: ## Show this help message
	@echo "Pnkln Core Stack - GKE + File Search Integration"
	@echo "=================================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

init: ## Initialize Terraform
	@echo "Initializing Terraform..."
	terraform init

plan: ## Show Terraform execution plan
	@echo "Planning Terraform changes..."
	terraform plan

apply: ## Apply Terraform configuration
	@echo "Applying Terraform configuration..."
	terraform apply

apply-auto: ## Apply Terraform configuration without confirmation
	@echo "Auto-applying Terraform configuration..."
	terraform apply -auto-approve

destroy: ## Destroy Terraform-managed infrastructure
	@echo "WARNING: This will destroy all infrastructure!"
	terraform destroy

validate: ## Validate Terraform configuration
	@echo "Validating Terraform configuration..."
	terraform validate

format: ## Format Terraform files
	@echo "Formatting Terraform files..."
	terraform fmt -recursive

clean: ## Clean Terraform artifacts
	@echo "Cleaning Terraform artifacts..."
	rm -rf .terraform/
	rm -f .terraform.lock.hcl
	rm -f terraform.tfstate*
	rm -f crash.log

status: ## Show Terraform state
	@echo "Terraform state:"
	terraform show

output: ## Show Terraform outputs
	@echo "Terraform outputs:"
	terraform output

# ============================================================================
# GKE OPERATIONS
# ============================================================================

gke-connect: ## Configure kubectl for GKE cluster
	@echo "Configuring kubectl..."
	gcloud container clusters get-credentials $(CLUSTER_NAME) \
		--region $(REGION) \
		--project $(PROJECT_ID)

gke-nodes: ## List GKE nodes
	@echo "GKE nodes:"
	kubectl get nodes

gke-pods: ## List all pods across namespaces
	@echo "All pods:"
	kubectl get pods --all-namespaces

# ============================================================================
# FILE SEARCH OPERATIONS
# ============================================================================

corpus-init: ## Initialize RAG corpora for all verticals
	@echo "Initializing RAG corpora..."
	./scripts/setup_file_search.sh --project $(PROJECT_ID) --region $(REGION)

corpus-list: ## List all RAG corpora
	@echo "Listing RAG corpora..."
	python3 scripts/corpus_import.py --list-corpora --project $(PROJECT_ID) --region $(REGION)

corpus-query: ## Test query (usage: make corpus-query VERTICAL=defense QUERY="your question")
	@if [ -z "$(VERTICAL)" ] || [ -z "$(QUERY)" ]; then \
		echo "Error: VERTICAL and QUERY required"; \
		echo "Usage: make corpus-query VERTICAL=defense QUERY=\"What are ITAR requirements?\""; \
		exit 1; \
	fi
	@echo "Querying $(VERTICAL) corpus..."
	python3 scripts/corpus_import.py \
		--vertical $(VERTICAL) \
		--query "$(QUERY)" \
		--project $(PROJECT_ID) \
		--region $(REGION)

# ============================================================================
# KUBERNETES DEPLOYMENTS
# ============================================================================

k8s-deploy: gke-connect ## Deploy Kubernetes manifests
	@echo "Deploying Kubernetes resources..."
	kubectl apply -f k8s-manifests/namespace.yaml
	kubectl apply -f k8s-manifests/deployment-example.yaml

k8s-delete: ## Delete Kubernetes deployments
	@echo "Deleting Kubernetes resources..."
	kubectl delete -f k8s-manifests/deployment-example.yaml --ignore-not-found
	kubectl delete -f k8s-manifests/namespace.yaml --ignore-not-found

k8s-logs: ## Show logs for orchestrator pods
	@echo "Orchestrator logs:"
	kubectl logs -f deployment/pnkln-orchestrator -n pnkln-core --tail=100

k8s-shell: ## Open shell in orchestrator pod
	@echo "Opening shell..."
	kubectl exec -it deployment/pnkln-orchestrator -n pnkln-core -- /bin/bash

# ============================================================================
# MONITORING
# ============================================================================

logs: ## Tail Cloud Logging
	@echo "Tailing cluster logs..."
	gcloud logging tail "resource.type=k8s_cluster AND resource.labels.cluster_name=$(CLUSTER_NAME)" \
		--project=$(PROJECT_ID)

metrics: ## Show File Search metrics
	@echo "File Search metrics:"
	gcloud monitoring time-series list \
		--filter='metric.type="aiplatform.googleapis.com/prediction/latencies"' \
		--project=$(PROJECT_ID) \
		--limit=10

dashboard: ## Open Cloud Monitoring dashboard
	@echo "Opening dashboard..."
	@echo "https://console.cloud.google.com/monitoring/dashboards?project=$(PROJECT_ID)"

# ============================================================================
# DEVELOPMENT
# ============================================================================

dev-setup: ## Setup development environment
	@echo "Setting up development environment..."
	python3 -m pip install --upgrade google-cloud-aiplatform google-cloud-storage
	gcloud auth application-default login

test: validate format ## Run tests (validate + format check)
	@echo "Running tests..."
	terraform fmt -check -recursive

docs: ## Generate documentation
	@echo "Generating documentation..."
	terraform-docs markdown table . > TERRAFORM_DOCS.md

# ============================================================================
# COST MANAGEMENT
# ============================================================================

cost-estimate: ## Show cost estimate
	@echo "Cost estimate:"
	@echo "GKE Cluster (3-10 nodes): $$200-500/month"
	@echo "Vertex AI: $$100-300/month"
	@echo "GCS Storage: $$50-100/month"
	@echo "Networking: $$50-150/month"
	@echo "Total: $$400-1050/month"

# ============================================================================
# QUICK DEPLOYMENT
# ============================================================================

deploy-all: init apply corpus-init k8s-deploy ## Full deployment: Terraform + Corpus + K8s
	@echo "Full deployment complete!"
	@echo "Next steps:"
	@echo "  1. Upload policy documents: gsutil cp policy.pdf gs://pnkln-policy-corpus-{vertical}/"
	@echo "  2. Import to corpus: make corpus-import VERTICAL=defense PATH=gs://..."
	@echo "  3. Monitor logs: make k8s-logs"
