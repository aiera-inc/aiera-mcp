# Makefile for Aiera MCP testing and development

.PHONY: help test test-unit test-integration test-fast test-slow test-domain test-coverage clean lint format install-dev

# Default target
help:
	@echo "Aiera MCP Development Commands"
	@echo "==============================="
	@echo ""
	@echo "Testing:"
	@echo "  test                 Run all tests (auto-detects uv)"
	@echo "  test-unit           Run unit tests only"
	@echo "  test-integration    Run integration tests only (requires API key)"
	@echo "  test-fast           Run fast tests only"
	@echo "  test-slow           Run slow tests only"
	@echo "  test-coverage       Run tests with coverage reporting"
	@echo "  test-domain DOMAIN  Run tests for specific domain"
	@echo ""
	@echo "uv-specific:"
	@echo "  uv-test             Run all tests with uv"
	@echo "  uv-test-unit        Run unit tests with uv"
	@echo "  uv-test-integration Run integration tests with uv (requires API key)"
	@echo "  uv-test-coverage    Run tests with coverage using uv"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint                Run linting checks"
	@echo "  format              Format code with black and isort"
	@echo "  type-check          Run type checking with mypy"
	@echo ""
	@echo "Development:"
	@echo "  install-dev         Install development dependencies"
	@echo "  clean               Clean build artifacts and cache"
	@echo "  server              Run MCP server locally"
	@echo ""
	@echo "Examples:"
	@echo "  make test-domain DOMAIN=events"
	@echo "  make test-integration AIERA_API_KEY=your-key"

# Test commands (automatically use uv if available)
test:
	@which uv > /dev/null 2>&1 && echo "Using uv..." || echo "Using system python..."
	python scripts/run_tests.py --type=all

test-unit:
	python scripts/run_tests.py --type=unit --verbose

test-integration:
	@if [ -z "$(AIERA_API_KEY)" ]; then \
		echo "❌ AIERA_API_KEY environment variable required for integration tests"; \
		echo "   Usage: make test-integration AIERA_API_KEY=your-key"; \
		exit 1; \
	fi
	AIERA_API_KEY=$(AIERA_API_KEY) python scripts/run_tests.py --type=integration --verbose

test-fast:
	python scripts/run_tests.py --type=fast

test-slow:
	python scripts/run_tests.py --type=slow

test-coverage:
	python scripts/run_tests.py --type=all --coverage
	@echo "Coverage report generated in htmlcov/index.html"

test-domain:
	@if [ -z "$(DOMAIN)" ]; then \
		echo "❌ DOMAIN parameter required"; \
		echo "   Usage: make test-domain DOMAIN=events"; \
		echo "   Available domains: events, filings, equities, company_docs, third_bridge, transcrippets"; \
		exit 1; \
	fi
	python scripts/run_tests.py --type=all --domain=$(DOMAIN) --verbose

# uv-specific commands
uv-test:
	uv run python scripts/run_tests.py --type=all

uv-test-unit:
	uv run python scripts/run_tests.py --type=unit --verbose

uv-test-integration:
	@if [ -z "$(AIERA_API_KEY)" ]; then \
		echo "❌ AIERA_API_KEY environment variable required for integration tests"; \
		echo "   Usage: make uv-test-integration AIERA_API_KEY=your-key"; \
		exit 1; \
	fi
	AIERA_API_KEY=$(AIERA_API_KEY) uv run python scripts/run_tests.py --type=integration --verbose

uv-test-coverage:
	uv run python scripts/run_tests.py --type=all --coverage

# Code quality
lint:
	@echo "Running flake8..."
	flake8 aiera_mcp tests --max-line-length=120 --ignore=E203,W503
	@echo "Running pylint..."
	pylint aiera_mcp --disable=C0114,C0115,C0116

format:
	@echo "Formatting with black..."
	black aiera_mcp tests scripts
	@echo "Sorting imports with isort..."
	isort aiera_mcp tests scripts

type-check:
	@echo "Running mypy type checking..."
	mypy aiera_mcp --ignore-missing-imports

# Development
install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

server:
	@echo "Starting MCP server..."
	@echo "Use Ctrl+C to stop"
	uv run python entrypoint.py

# CI/CD helpers
ci-test:
	python scripts/run_tests.py --type=unit --coverage --parallel=2

ci-integration:
	@if [ -z "$(AIERA_API_KEY)" ]; then \
		echo "⚠️  Skipping integration tests - no API key provided"; \
	else \
		python scripts/run_tests.py --type=integration --parallel=1; \
	fi

# Quality gates
quality-gate: lint type-check test-unit
	@echo "✅ Quality gate passed!"

# Docker helpers (if needed)
docker-test:
	docker build -t aiera-mcp-test -f Dockerfile.test .
	docker run --rm -e AIERA_API_KEY=$(AIERA_API_KEY) aiera-mcp-test

# Performance testing
perf-test:
	@echo "Running performance tests..."
	python scripts/run_tests.py --type=slow --verbose

# Test data management
setup-test-data:
	@echo "Setting up test data..."
	python scripts/setup_test_fixtures.py

# Documentation
docs:
	@echo "Generating documentation..."
	sphinx-build -b html docs docs/_build

# Database/fixture management
update-fixtures:
	@echo "Updating test fixtures from API..."
	@if [ -z "$(AIERA_API_KEY)" ]; then \
		echo "❌ AIERA_API_KEY required to update fixtures"; \
		exit 1; \
	fi
	AIERA_API_KEY=$(AIERA_API_KEY) python scripts/update_fixtures.py

# Benchmarking
benchmark:
	@echo "Running benchmarks..."
	python -m pytest tests/benchmark --benchmark-only

# Security
security-scan:
	@echo "Running security scan..."
	bandit -r aiera_mcp -f json -o security-report.json

# Full pipeline
full-test: clean quality-gate test-coverage
	@echo "🎉 Full test pipeline completed!"