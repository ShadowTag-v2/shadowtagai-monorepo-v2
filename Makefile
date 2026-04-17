.PHONY: test lint format clean check all

# Run the full test suite
test:
	python3 -m pytest tests/ -v --tb=short

# Run test suite with coverage (60% minimum threshold)
coverage:
	python3 -m pytest tests/ -v --tb=short --cov=control/pnkln --cov=scripts --cov-report=term-missing --cov-fail-under=60

# Dead code sweep (with whitelist for false positives)
vulture:
	python3 -m vulture control/pnkln/ scripts/ .vulture_whitelist.py --min-confidence 80

# Lint check (no fix)
lint:
	python3 -m ruff check control/pnkln/ scripts/

# Lint fix (safe)
fix:
	python3 -m ruff check --fix control/pnkln/ scripts/

# Format code
format:
	python3 -m ruff format control/pnkln/ scripts/

# GCA pruner dry-run
prune-check:
	python3 scripts/prune_gca_chat_threads.py

# Full quality gate: format + fix + test + vulture
check: format fix test vulture
	@echo "✅ All quality checks passed"

# Clean build artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true

# Everything
all: format fix test vulture
	@echo "🎉 Full sweep complete"
