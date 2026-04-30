# Terraform/Terragrunt Makefile
# Common operations for the IaC catalog

.PHONY: init plan apply validate lint checkov fmt docs clean

SHELL := /bin/bash
TG := terragrunt
TF := tofu
CATALOG := infrastructure-catalog-gcp-cloud-run
LIVE := infrastructure-live-gcp

# ─── Module Development ────────────────────────────────
validate: ## Validate all modules
	@echo "Validating catalog modules..."
	@for dir in $(CATALOG)/*/; do \
		echo "→ $$dir"; \
		cd $$dir && $(TF) init -backend=false -no-color >/dev/null 2>&1 && $(TF) validate && cd ../..; \
	done

fmt: ## Format all Terraform files
	$(TF) fmt -recursive $(CATALOG)/
	$(TF) fmt -recursive $(LIVE)/

lint: checkov ## Alias for checkov

checkov: ## Run Checkov security scan
	checkov -d $(CATALOG)/ --framework terraform --quiet --compact

docs: ## Generate terraform-docs for all modules
	@for dir in $(CATALOG)/*/; do \
		echo "→ Generating docs for $$dir"; \
		terraform-docs markdown $$dir > $$dir/README.md 2>/dev/null || true; \
	done

# ─── Terragrunt Operations ─────────────────────────────
init: ## Initialize Terragrunt (all environments)
	cd $(LIVE)/prod && $(TG) init --terragrunt-non-interactive

plan: ## Plan prod changes
	cd $(LIVE)/prod && $(TG) run-all plan --terragrunt-non-interactive

apply: ## Apply prod changes (requires confirmation)
	cd $(LIVE)/prod && $(TG) run-all apply

plan-staging: ## Plan staging changes
	cd $(LIVE)/staging && $(TG) run-all plan --terragrunt-non-interactive

apply-staging: ## Apply staging changes
	cd $(LIVE)/staging && $(TG) run-all apply

# ─── Utility ───────────────────────────────────────────
clean: ## Clean Terraform caches
	find . -name ".terraform" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".terragrunt-cache" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.tfstate.backup" -delete 2>/dev/null || true

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
