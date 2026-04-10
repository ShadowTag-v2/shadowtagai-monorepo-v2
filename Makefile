# ==============================================================================
# Monorepo Uphillsnowball - Agent Command Center
# ==============================================================================

# Variables (Paths)
BACKEND_DIR = apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services
FRONTEND_DIR = apps/shadowtag-omega-v4-web-dashboard

# Default target when just running `make`
.PHONY: help
help:
	@echo "🤖 Antigravity Agent Makefile 🤖"
	@echo "----------------------------------------------------------------------"
	@echo "Usage: make [target]"
	@echo ""
	@echo "Setup & Run:"
	@echo "  setup         - Install all backend and frontend dependencies"
	@echo "  up            - Spin up the entire stack (DB, API, Web) via Docker"
	@echo "  down          - Tear down the Docker stack"
	@echo "  dev-api       - Run the FastAPI backend locally (hot-reload)"
	@echo "  dev-web       - Run the Next.js frontend locally (hot-reload)"
	@echo ""
	@echo "Database (Alembic):"
	@echo "  db-migrate    - Auto-generate a new migration (reads your models.py)"
	@echo "  db-upgrade    - Apply pending migrations to the database"
	@echo ""
	@echo "Quality Assurance:"
	@echo "  lint          - Run Ruff linter and basedpyright type checker"
	@echo "  format        - Auto-format Python code using Ruff"
	@echo "  test          - Run the backend test suite via pytest"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean         - Remove caches, pycache, and temporary files"
	@echo "----------------------------------------------------------------------"

# ==============================================================================
# Setup & Execution
# ==============================================================================
.PHONY: setup
setup:
	@echo "📦 Installing Backend Dependencies..."
	cd $(BACKEND_DIR) && uv sync
	@echo "📦 Installing Frontend Dependencies..."
	cd $(FRONTEND_DIR) && npm install

.PHONY: up
up:
	@echo "🐳 Starting the Docker Compose stack..."
	docker compose up --build -d

.PHONY: down
down:
	@echo "🛑 Stopping the Docker Compose stack..."
	docker compose down

.PHONY: dev-api
dev-api:
	@echo "🚀 Starting FastAPI Development Server..."
	cd $(BACKEND_DIR) && source ../../../.venv/bin/activate && uvicorn ag_ui_server:app --reload --host 127.0.0.1 --port 8000

.PHONY: dev-web
dev-web:
	@echo "🌐 Starting Next.js Development Server..."
	cd $(FRONTEND_DIR) && npm run dev

# ==============================================================================
# Database Migrations
# ==============================================================================
.PHONY: db-migrate
db-migrate:
	@echo "📝 Generating new Alembic migration..."
	cd $(BACKEND_DIR) && source ../../../.venv/bin/activate && alembic revision --autogenerate -m "agent_auto_migration"

.PHONY: db-upgrade
db-upgrade:
	@echo "⬆️ Applying Alembic migrations..."
	cd $(BACKEND_DIR) && source ../../../.venv/bin/activate && alembic upgrade head

# ==============================================================================
# Quality Assurance
# ==============================================================================
.PHONY: lint
lint:
	@echo "🧹 Linting code..."
	cd $(BACKEND_DIR) && source ../../../.venv/bin/activate && ruff check .
	cd $(BACKEND_DIR) && source ../../../.venv/bin/activate && basedpyright

.PHONY: format
format:
	@echo "🎨 Formatting code..."
	cd $(BACKEND_DIR) && source ../../../.venv/bin/activate && ruff format .

.PHONY: test
test:
	@echo "🧪 Running Pytest..."
	cd $(BACKEND_DIR) && source ../../../.venv/bin/activate && pytest

# ==============================================================================
# Cleanup
# ==============================================================================
.PHONY: clean
clean:
	@echo "🗑️ Cleaning up cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".basedpyright" -exec rm -rf {} +
	@echo "✅ Cleanup complete."
