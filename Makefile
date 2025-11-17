.PHONY: help install install-dev test test-cov lint format clean docker-up docker-down docker-logs db-migrate db-upgrade db-downgrade seed-db run-backend run-frontend build deploy docs audit security check-all

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip3
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
MYPY := mypy
ISORT := isort
DOCKER_COMPOSE := docker-compose
ALEMBIC := alembic

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ Help

help: ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(BLUE)Usage:$(NC)\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Installation

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	cd backend && $(PIP) install -r requirements.txt
	cd frontend && npm install
	@echo "$(GREEN)✓ Production dependencies installed$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	cd backend && $(PIP) install -r requirements.txt -r requirements-dev.txt
	cd frontend && npm install
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

##@ Development

run-backend: ## Run backend development server
	@echo "$(BLUE)Starting backend server...$(NC)"
	cd backend && uvicorn main:app --reload --port 8000

run-frontend: ## Run frontend development server
	@echo "$(BLUE)Starting frontend server...$(NC)"
	cd frontend && npm start

run-all: ## Run both backend and frontend (requires tmux or run in separate terminals)
	@echo "$(YELLOW)Note: Run 'make run-backend' and 'make run-frontend' in separate terminals$(NC)"

##@ Testing

test: ## Run all tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd backend && $(PYTEST) -v
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && npm test -- --watchAll=false
	@echo "$(GREEN)✓ All tests passed$(NC)"

test-backend: ## Run backend tests only
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd backend && $(PYTEST) -v

test-frontend: ## Run frontend tests only
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && npm test -- --watchAll=false

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	cd backend && $(PYTEST) --cov=. --cov-report=html --cov-report=term --cov-report=xml
	@echo "$(GREEN)✓ Coverage report generated in backend/htmlcov/$(NC)"

test-watch: ## Run tests in watch mode
	cd backend && $(PYTEST) -v --looponfail

test-compliance: ## Run compliance engine tests only
	cd backend && $(PYTEST) tests/test_compliance_engine.py -v

##@ Code Quality

lint: ## Run all linters
	@echo "$(BLUE)Running linters...$(NC)"
	cd backend && $(FLAKE8) .
	cd backend && $(MYPY) . --ignore-missing-imports
	cd frontend && npm run lint
	@echo "$(GREEN)✓ Linting complete$(NC)"

lint-backend: ## Lint backend code
	cd backend && $(FLAKE8) .
	cd backend && $(MYPY) . --ignore-missing-imports

lint-frontend: ## Lint frontend code
	cd frontend && npm run lint

format: ## Auto-format all code
	@echo "$(BLUE)Formatting code...$(NC)"
	cd backend && $(BLACK) .
	cd backend && $(ISORT) .
	cd frontend && npm run format || true
	@echo "$(GREEN)✓ Code formatted$(NC)"

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code format...$(NC)"
	cd backend && $(BLACK) --check .
	cd backend && $(ISORT) --check .

##@ Docker

docker-up: ## Start all Docker containers
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Containers started$(NC)"
	@echo "$(YELLOW)Run 'make docker-logs' to view logs$(NC)"

docker-down: ## Stop all Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Containers stopped$(NC)"

docker-down-volumes: ## Stop containers and remove volumes
	@echo "$(RED)Stopping containers and removing volumes...$(NC)"
	$(DOCKER_COMPOSE) down -v
	@echo "$(GREEN)✓ Containers and volumes removed$(NC)"

docker-logs: ## View Docker container logs
	$(DOCKER_COMPOSE) logs -f

docker-logs-backend: ## View backend container logs
	$(DOCKER_COMPOSE) logs -f backend

docker-logs-postgres: ## View PostgreSQL container logs
	$(DOCKER_COMPOSE) logs -f postgres

docker-build: ## Rebuild Docker containers
	@echo "$(BLUE)Rebuilding Docker containers...$(NC)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✓ Containers rebuilt$(NC)"

docker-restart: ## Restart all containers
	@echo "$(BLUE)Restarting containers...$(NC)"
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✓ Containers restarted$(NC)"

docker-ps: ## List running containers
	$(DOCKER_COMPOSE) ps

docker-shell-backend: ## Open shell in backend container
	$(DOCKER_COMPOSE) exec backend /bin/bash

docker-shell-db: ## Open PostgreSQL shell
	$(DOCKER_COMPOSE) exec postgres psql -U postgres -d acagp

##@ Database

db-migrate: ## Create new database migration
	@read -p "Enter migration message: " msg; \
	cd backend && $(ALEMBIC) revision --autogenerate -m "$$msg"
	@echo "$(GREEN)✓ Migration created$(NC)"

db-upgrade: ## Apply database migrations
	@echo "$(BLUE)Applying database migrations...$(NC)"
	cd backend && $(ALEMBIC) upgrade head
	@echo "$(GREEN)✓ Migrations applied$(NC)"

db-downgrade: ## Rollback last migration
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	cd backend && $(ALEMBIC) downgrade -1
	@echo "$(GREEN)✓ Migration rolled back$(NC)"

db-history: ## Show migration history
	cd backend && $(ALEMBIC) history

db-current: ## Show current migration version
	cd backend && $(ALEMBIC) current

db-reset: ## Reset database (WARNING: destroys data)
	@echo "$(RED)WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		$(DOCKER_COMPOSE) down -v; \
		$(DOCKER_COMPOSE) up -d postgres; \
		sleep 5; \
		cd backend && $(ALEMBIC) upgrade head; \
		echo "$(GREEN)✓ Database reset complete$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

seed-db: ## Seed database with example data
	@echo "$(BLUE)Seeding database...$(NC)"
	cd backend && $(PYTHON) -m scripts.seed_data
	@echo "$(GREEN)✓ Database seeded$(NC)"

##@ Build

build-backend: ## Build backend Docker image
	docker build -f infrastructure/docker/Dockerfile.backend -t acagp-backend:latest backend/

build-frontend: ## Build frontend for production
	cd frontend && npm run build
	@echo "$(GREEN)✓ Frontend built in frontend/build/$(NC)"

build-all: build-backend build-frontend ## Build all components

##@ Deployment

deploy-staging: ## Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(NC)"
	@echo "$(YELLOW)Staging deployment not yet configured$(NC)"

deploy-production: ## Deploy to production environment
	@echo "$(BLUE)Deploying to production...$(NC)"
	@echo "$(YELLOW)Production deployment not yet configured$(NC)"

##@ Documentation

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "$(YELLOW)Documentation generation not yet implemented$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	@echo "$(YELLOW)Documentation server not yet implemented$(NC)"

##@ Security & Audit

audit: ## Run security audit on dependencies
	@echo "$(BLUE)Running security audit...$(NC)"
	cd backend && pip-audit || echo "$(YELLOW)pip-audit not installed. Run: pip install pip-audit$(NC)"
	cd frontend && npm audit
	@echo "$(GREEN)✓ Audit complete$(NC)"

audit-fix: ## Fix security vulnerabilities automatically
	@echo "$(BLUE)Fixing vulnerabilities...$(NC)"
	cd frontend && npm audit fix
	@echo "$(YELLOW)Review backend/requirements.txt for updates$(NC)"

security-scan: ## Run security scan with Trivy
	@echo "$(BLUE)Running security scan...$(NC)"
	trivy fs --security-checks vuln . || echo "$(YELLOW)Trivy not installed. Visit: https://aquasecurity.github.io/trivy/$(NC)"

##@ Utilities

clean: ## Clean build artifacts and cache files
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name 'htmlcov' -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/.coverage
	rm -rf frontend/build
	rm -rf frontend/node_modules/.cache
	@echo "$(GREEN)✓ Cleaned$(NC)"

clean-all: clean docker-down-volumes ## Clean everything including Docker volumes
	@echo "$(GREEN)✓ Deep clean complete$(NC)"

check-all: format lint test ## Run all quality checks
	@echo "$(GREEN)✓ All checks passed$(NC)"

pre-commit: format lint test-backend ## Run pre-commit checks
	@echo "$(GREEN)✓ Pre-commit checks passed$(NC)"

init: install-dev docker-up db-upgrade seed-db ## Initialize project for first-time setup
	@echo "$(GREEN)✓ Project initialized$(NC)"
	@echo "$(BLUE)Backend:$(NC) http://localhost:8000"
	@echo "$(BLUE)Frontend:$(NC) http://localhost:3000"
	@echo "$(BLUE)API Docs:$(NC) http://localhost:8000/docs"

status: ## Show project status
	@echo "$(BLUE)=== Project Status ===$(NC)"
	@echo "$(GREEN)Backend:$(NC)"
	@curl -s http://localhost:8000/health 2>/dev/null | python -m json.tool || echo "  $(RED)✗ Not running$(NC)"
	@echo "\n$(GREEN)Frontend:$(NC)"
	@curl -s http://localhost:3000 > /dev/null 2>&1 && echo "  $(GREEN)✓ Running$(NC)" || echo "  $(RED)✗ Not running$(NC)"
	@echo "\n$(GREEN)Database:$(NC)"
	@$(DOCKER_COMPOSE) ps postgres | grep "Up" > /dev/null 2>&1 && echo "  $(GREEN)✓ Running$(NC)" || echo "  $(RED)✗ Not running$(NC)"

version: ## Show version information
	@echo "$(BLUE)ACAGP Version:$(NC) 1.0.0"
	@echo "$(BLUE)Python:$(NC) $$($(PYTHON) --version 2>&1)"
	@echo "$(BLUE)Node:$(NC) $$(node --version 2>&1)"
	@echo "$(BLUE)Docker:$(NC) $$(docker --version 2>&1)"
	@echo "$(BLUE)Docker Compose:$(NC) $$(docker-compose --version 2>&1)"

##@ Quick Commands

quick-test: ## Quick test (backend only, no coverage)
	cd backend && $(PYTEST) -x

quick-start: docker-up ## Quick start all services
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "Visit: http://localhost:8000/docs"

quick-stop: docker-down ## Quick stop all services
	@echo "$(GREEN)✓ Services stopped$(NC)"

quick-reset: docker-down docker-up db-upgrade ## Quick reset environment
	@echo "$(GREEN)✓ Environment reset$(NC)"
