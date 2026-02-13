.PHONY: help install test lint format security clean all

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install package and dev dependencies
	pip install -e .
	pip install pytest pytest-asyncio pytest-cov ruff black isort mypy bandit safety

test: ## Run tests with coverage
	pytest tests/ --cov=src/tourney_threads --cov-report=term-missing --cov-report=html

test-fast: ## Run tests without coverage (faster)
	pytest tests/ -v

lint: ## Run all linters
	ruff check src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/
	mypy src/

format: ## Auto-format code
	black src/ tests/
	isort src/ tests/
	ruff check --fix src/ tests/

security: ## Run security checks
	bandit -r src/ -ll
	safety check

type-check: ## Run type checking
	mypy src/ --ignore-missing-imports

ci: lint test ## Run all CI checks locally
	@echo "All CI checks passed!"

clean: ## Clean build artifacts and cache
	rm -rf build dist *.egg-info .pytest_cache .coverage htmlcov .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

all: format lint test ## Format, lint, and test
	@echo "All checks complete!"
