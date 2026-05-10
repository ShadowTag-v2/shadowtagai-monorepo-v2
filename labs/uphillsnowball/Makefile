# Makefile — Uphill Snowball Sovereign Operating System
#
# Build targets for every language in the polyglot stack:
#   - Python (Temporal workers, AST fabric, intelligence engines)
#   - Go (Cor.Go ZTA kernel)
#   - C++ (Midas IPC muscle)
#   - Docker (sealed multi-stage container)
#   - Flutter (mobile edge client)

.PHONY: all docker dev test lint clean go-build cpp-build help

# ── Default ────────────────────────────────────────────────────
all: lint test

# ── Docker Build ───────────────────────────────────────────────
docker:
	docker build -t pnkln-omega:latest .

# ── Cor.Go ZTA Kernel ──────────────────────────────────────────
go-build:
	cd cmd/cor-go && go build -o ../../bin/judge6_pep .

# ── Midas C++ IPC Client ──────────────────────────────────────
cpp-build:
	g++ -std=c++17 -O2 -o bin/midas_ipc src/native/core/midas_ipc_client.cpp -lzmq

# ── Python Dev Server (Temporal Worker) ────────────────────────
dev:
	python -m src.worker

# ── Test Suite ─────────────────────────────────────────────────
test:
	pytest tests/ -v --tb=short

# ── Lint & Format ──────────────────────────────────────────────
lint:
	ruff check src/ --fix
	ruff check src/ --select F401,F841 --statistics || true

# ── Clean Build Artifacts ──────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + || true
	find . -type f -name '*.pyc' -delete || true
	rm -rf bin/ .pytest_cache/ .ruff_cache/

# ── Help ───────────────────────────────────────────────────────
help:
	@echo "pnkln V.OMEGA Makefile"
	@echo ""
	@echo "  make docker      - Build the sealed Docker container"
	@echo "  make go-build    - Compile Cor.Go ZTA kernel"
	@echo "  make cpp-build   - Compile Midas C++ IPC client"
	@echo "  make dev         - Start Temporal worker"
	@echo "  make test        - Run test suite"
	@echo "  make lint        - Lint + dead code sweep"
	@echo "  make clean       - Clean build artifacts"
