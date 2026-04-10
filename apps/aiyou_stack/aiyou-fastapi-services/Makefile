.PHONY: help deploy destroy status logs workbench cost-estimate sla-check clean

# Default target
.DEFAULT_GOAL := help

# Configuration
PROJECT_ID ?= $(shell gcloud config get-value project)
REGION ?= us-central1
ZONE ?= us-central1-a
CLUSTER_NAME ?= pnkln-inference
NAMESPACE ?= pnkln-inference

################################################################################
# Help
################################################################################

help: ## Show this help message
	@echo ''
	@echo 'Usage:'
	@echo '  make <target>'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''
	@echo 'Environment Variables:'
	@echo '  PROJECT_ID      GCP project ID (current: $(PROJECT_ID))'
	@echo '  REGION          GCP region (current: $(REGION))'
	@echo '  CLUSTER_NAME    GKE cluster name (current: $(CLUSTER_NAME))'
	@echo ''

################################################################################
# Deployment
################################################################################

deploy: ## Deploy complete infrastructure (30-45 min)
	@echo "Starting deployment to project: $(PROJECT_ID)"
	@if [ -z "$(PROJECT_ID)" ]; then \
		echo "ERROR: PROJECT_ID not set. Run: make deploy PROJECT_ID=your-project-id"; \
		exit 1; \
	fi
	@export PNKLN_PROJECT_ID=$(PROJECT_ID) && ./pnkln-gke-deploy.sh

deploy-terraform: ## Deploy using Terraform (alternative)
	@echo "Deploying with Terraform..."
	@cd terraform && \
		terraform init && \
		terraform plan -var="project_id=$(PROJECT_ID)" -out=tfplan && \
		terraform apply tfplan

deploy-judge: ## Deploy Judge #6 service only
	@echo "Deploying Judge #6..."
	@kubectl apply -f judge-deployment.yaml

################################################################################
# Infrastructure Management
################################################################################

destroy: ## Destroy all infrastructure (WARNING: irreversible)
	@echo "WARNING: This will destroy all infrastructure!"
	@read -p "Type 'yes' to confirm: " confirm && [ "$$confirm" = "yes" ]
	@cd terraform && terraform destroy -var="project_id=$(PROJECT_ID)"
	@gcloud container clusters delete $(CLUSTER_NAME) --region=$(REGION) --quiet

destroy-terraform: ## Destroy Terraform-managed resources only
	@cd terraform && terraform destroy -var="project_id=$(PROJECT_ID)"

################################################################################
# Monitoring & Status
################################################################################

status: ## Show cluster and deployment status
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  CLUSTER STATUS"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@gcloud container clusters describe $(CLUSTER_NAME) --region=$(REGION) \
		--format="table(name,status,currentNodeCount,location)" || true
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  NODE POOLS"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@gcloud container node-pools list --cluster=$(CLUSTER_NAME) --region=$(REGION) \
		--format="table(name,status,machineType,autoscaling.enabled)" || true
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  PODS (namespace: $(NAMESPACE))"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@kubectl get pods -n $(NAMESPACE) -o wide || echo "Namespace not found"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  SERVICES"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@kubectl get svc -n $(NAMESPACE) || echo "Namespace not found"

logs: ## Show Judge #6 logs
	@kubectl logs -n $(NAMESPACE) -l app=pnkln-judge --tail=100 -f

logs-errors: ## Show error logs only
	@kubectl logs -n $(NAMESPACE) -l app=pnkln-judge --tail=500 | grep -i error

sla-check: ## Run single SLA compliance check
	@./monitor-sla.sh --once

sla-monitor: ## Start continuous SLA monitoring
	@./monitor-sla.sh --continuous

################################################################################
# Cost Management
################################################################################

cost-estimate: ## Estimate infrastructure costs
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  COST ESTIMATE"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "Development Environment (1 GPU node):"
	@echo "  CPU pool (1 node):      $$11.42/day"
	@echo "  GPU pool (1 node):      $$26.16/day"
	@echo "  Vertex Workbench:       $$22.80/day"
	@echo "  ─────────────────────────────────────"
	@echo "  TOTAL:                  ~$$60/day ($$1,800/month)"
	@echo ""
	@echo "Production Environment (5 GPU nodes):"
	@echo "  CPU pool (1 node):      $$11.42/day"
	@echo "  GPU pool (5 nodes):     $$130.80/day"
	@echo "  Vertex Workbench:       $$22.80/day"
	@echo "  ─────────────────────────────────────"
	@echo "  TOTAL:                  ~$$165/day ($$4,950/month)"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  LIMITS"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Dev limit:              $$50/day"
	@echo "  Prod limit:             $$500/day (kill-switch)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "Set up billing alerts:"
	@echo "  https://console.cloud.google.com/billing"

cost-actual: ## Show actual costs from billing
	@gcloud billing projects describe $(PROJECT_ID) || echo "Billing not configured"

################################################################################
# Vertex AI Workbench
################################################################################

workbench: ## Access Vertex AI Workbench
	@echo "Opening Vertex AI Workbench..."
	@echo ""
	@gcloud notebooks instances describe pnkln-dev-workbench --location=$(ZONE) || \
		echo "Workbench not found. Deploy first: make deploy"
	@echo ""
	@echo "Access URL:"
	@echo "  https://console.cloud.google.com/vertex-ai/workbench/user-managed?project=$(PROJECT_ID)"

workbench-ssh: ## SSH into Workbench instance
	@gcloud notebooks instances ssh pnkln-dev-workbench --location=$(ZONE)

################################################################################
# Configuration
################################################################################

configure-kubectl: ## Configure kubectl for GKE cluster
	@gcloud container clusters get-credentials $(CLUSTER_NAME) \
		--region=$(REGION) \
		--project=$(PROJECT_ID)
	@echo "kubectl configured for cluster: $(CLUSTER_NAME)"

update-secrets: ## Update API keys in Secret Manager
	@echo "Updating API keys..."
	@echo ""
	@echo "Anthropic API key:"
	@read -s -p "Enter key (or press Enter to skip): " key && \
		if [ -n "$$key" ]; then \
			echo -n "$$key" | gcloud secrets versions add anthropic-api-key --data-file=-; \
		fi
	@echo ""
	@echo "OpenAI API key:"
	@read -s -p "Enter key (or press Enter to skip): " key && \
		if [ -n "$$key" ]; then \
			echo -n "$$key" | gcloud secrets versions add openai-api-key --data-file=-; \
		fi
	@echo ""
	@echo "xAI API key:"
	@read -s -p "Enter key (or press Enter to skip): " key && \
		if [ -n "$$key" ]; then \
			echo -n "$$key" | gcloud secrets versions add xai-api-key --data-file=-; \
		fi
	@echo ""
	@echo "Secrets updated successfully!"

list-secrets: ## List Secret Manager secrets
	@gcloud secrets list --filter="labels.app=pnkln-inference"

################################################################################
# Debugging
################################################################################

debug-pods: ## Show detailed pod information
	@kubectl describe pods -n $(NAMESPACE) -l app=pnkln-judge

debug-events: ## Show recent cluster events
	@kubectl get events -n $(NAMESPACE) --sort-by='.lastTimestamp'

debug-hpa: ## Show HPA status
	@kubectl get hpa -n $(NAMESPACE)
	@kubectl describe hpa pnkln-judge-hpa -n $(NAMESPACE)

shell: ## Open shell in Judge pod
	@kubectl exec -it -n $(NAMESPACE) \
		$$(kubectl get pod -n $(NAMESPACE) -l app=pnkln-judge -o jsonpath='{.items[0].metadata.name}') \
		-- /bin/sh

port-forward: ## Port-forward to Judge service
	@echo "Port-forwarding Judge service to localhost:8080..."
	@kubectl port-forward -n $(NAMESPACE) svc/pnkln-judge 8080:80

################################################################################
# Testing
################################################################################

test-endpoint: ## Test Judge endpoint (requires port-forward)
	@echo "Testing Judge endpoint..."
	@curl -X POST http://localhost:8080/infer \
		-H "Content-Type: application/json" \
		-d '{"prompt":"What is 2+2?","max_tokens":50}' | jq .

load-test: ## Run load test (100 requests)
	@echo "Running load test..."
	@for i in $$(seq 1 100); do \
		curl -s -X POST http://localhost:8080/infer \
			-H "Content-Type: application/json" \
			-d '{"prompt":"Test $$i","max_tokens":20}' > /dev/null & \
	done; \
	wait; \
	echo "Load test complete"

################################################################################
# Cleanup
################################################################################

clean: ## Clean temporary files
	@echo "Cleaning temporary files..."
	@rm -f tfplan
	@rm -f /tmp/pnkln-*.log
	@echo "Clean complete"

clean-terraform: ## Clean Terraform state
	@cd terraform && rm -rf .terraform terraform.tfstate* tfplan

restart-judge: ## Restart Judge deployment
	@kubectl rollout restart deployment/pnkln-judge -n $(NAMESPACE)
	@kubectl rollout status deployment/pnkln-judge -n $(NAMESPACE)

scale-judge: ## Scale Judge deployment (usage: make scale-judge REPLICAS=5)
	@kubectl scale deployment/pnkln-judge -n $(NAMESPACE) --replicas=$(REPLICAS)

################################################################################
# Documentation
################################################################################

docs: ## Open documentation
	@echo "Documentation:"
	@echo "  - README: ./README.md"
	@echo "  - Deployment Summary: ./DEPLOYMENT_SUMMARY.txt"
	@echo "  - GKE Best Practices: https://cloud.google.com/kubernetes-engine/docs/best-practices"
	@echo "  - Vertex AI: https://cloud.google.com/vertex-ai/docs"

version: ## Show version information
	@echo "Pnkln GKE Deployment Package v1.0.0"
	@echo ""
	@echo "Component versions:"
	@echo "  - GKE version: $$(gcloud container get-server-config --region=$(REGION) --format='value(defaultClusterVersion)' 2>/dev/null || echo 'unknown')"
	@echo "  - kubectl: $$(kubectl version --client --short 2>/dev/null || echo 'unknown')"
	@echo "  - gcloud: $$(gcloud version --format='value(core)' 2>/dev/null || echo 'unknown')"
	@echo "  - terraform: $$(terraform version -json 2>/dev/null | jq -r '.terraform_version' || echo 'not installed')"
