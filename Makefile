# AiYou Governance System - Makefile
# Elegant automation for the pnkln way

.PHONY: help install test lint format clean docker-build docker-push deploy

# Default target
help:
	@echo "AiYou Governance System - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters (ruff, mypy)"
	@echo "  make format        - Format code (black, ruff)"
	@echo "  make run           - Run locally"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-push   - Push to GCR"
	@echo "  make docker-run    - Run in Docker locally"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy-dev    - Deploy to dev GKE"
	@echo "  make deploy-prod   - Deploy to production GKE"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make logs          - Tail GKE logs"

# ============================================================================
# Development
# ============================================================================

install:
	pip install -r requirements.txt
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:
	ruff check src/
	mypy src/

format:
	black src/ tests/
	ruff check --fix src/ tests/

run:
	python -m uvicorn src.gateway.main:app --reload --host 0.0.0.0 --port 8000

# ============================================================================
# Docker
# ============================================================================

PROJECT_ID ?= $(shell gcloud config get-value project)
IMAGE_NAME = governance-gateway
IMAGE_TAG ?= latest
GCR_IMAGE = gcr.io/$(PROJECT_ID)/$(IMAGE_NAME):$(IMAGE_TAG)

docker-build:
	@echo "Building Docker image: $(GCR_IMAGE)"
	docker build -t $(GCR_IMAGE) .

docker-push: docker-build
	@echo "Pushing to GCR: $(GCR_IMAGE)"
	docker push $(GCR_IMAGE)

docker-run:
	docker run --rm -p 8000:8000 --env-file .env $(GCR_IMAGE)

# ============================================================================
# GKE Deployment
# ============================================================================

deploy-dev: docker-push
	@echo "Deploying to development GKE..."
	kubectl apply -k k8s/namespaces/
	kubectl apply -k k8s/deployments/
	kubectl rollout status deployment/governance-gateway -n governance

deploy-prod: docker-push
	@echo "Deploying to production GKE..."
	@echo "⚠️  WARNING: This will deploy to PRODUCTION"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		kubectl apply -k k8s/namespaces/; \
		kubectl apply -k k8s/deployments/; \
		kubectl rollout status deployment/governance-gateway -n governance; \
	fi

logs:
	kubectl logs -f -n governance -l app=governance-gateway --tail=100

# ============================================================================
# Utilities
# ============================================================================

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ htmlcov/ .coverage

.PHONY: install test lint format clean run docker-build docker-push docker-run deploy-dev deploy-prod logs
