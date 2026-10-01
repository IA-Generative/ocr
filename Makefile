# =============================================================================
# OCR API — developer entrypoint
#
# `make` (or `make help`) lists every target grouped by topic.
# =============================================================================

# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------

# Colors for terminal output
COLOR_RESET   := \033[0m
COLOR_BOLD    := \033[1m
COLOR_DIM     := \033[2m
COLOR_RED     := \033[31m
COLOR_GREEN   := \033[32m
COLOR_YELLOW  := \033[33m
COLOR_BLUE    := \033[34m
COLOR_CYAN    := \033[36m

# Paths
PROJECT_ROOT   := $(shell pwd)
SERVER_DIR     := $(PROJECT_ROOT)/apps/server
CLIENT_DIR     := $(PROJECT_ROOT)/apps/client
SDK_DIR        := $(PROJECT_ROOT)/sdk/python

# Compose files
COMPOSE_DEV      := $(PROJECT_ROOT)/docker-compose.yaml
COMPOSE_TEST     := $(PROJECT_ROOT)/docker-compose-test.yaml
COMPOSE_FRONT    := $(PROJECT_ROOT)/docker-compose.frontend.yaml
COMPOSE_LITEPARSE := $(PROJECT_ROOT)/docker-compose-liteparse-test.override.yaml

# Compose *service* names (not container_name — `docker compose` addresses services)
SVC_BACKEND    := ocr_backend
SVC_SERVICE    := ocr_service
SVC_FRONTEND   := ocr_frontend
SVC_MIGRATION  := migration

# Runtime
DOCKER_COMPOSE := docker compose
UV             := uv
PNPM           := pnpm
PYTHONPATH     := $(PROJECT_ROOT)

# Backend dependency groups installed by `make install`
UV_GROUPS      := --group test --group ocr-backend --group ocr-service-paddle

STRESS_HOST    := http://localhost:5000
HAS_GPU        := $(shell nvidia-smi > /dev/null 2>&1 && echo yes || echo no)

.DEFAULT_GOAL := help

# Guard: fail with an actionable message instead of a cryptic "command not found".
define _require
	@command -v $(1) >/dev/null 2>&1 || { \
		echo "$(COLOR_RED)✗$(COLOR_RESET) $(1) is required but not installed. $(2)"; \
		exit 1; \
	}
endef

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------

.PHONY: help
help: ## Show this help message
	@echo ""
	@echo "$(COLOR_BOLD)$(COLOR_CYAN)  OCR API — available commands$(COLOR_RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} \
		/^## / { printf "\n$(COLOR_BOLD)$(COLOR_YELLOW)%s$(COLOR_RESET)\n", substr($$0, 4) } \
		/^[a-zA-Z0-9_.-]+:.*##/ { printf "  $(COLOR_CYAN)%-32s$(COLOR_RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

# -----------------------------------------------------------------------------
## ▸ Setup
# -----------------------------------------------------------------------------

.PHONY: install
install: install-backend install-frontend install-hooks ## Install everything (backend, frontend, git hooks)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)  ✓ Workspace ready$(COLOR_RESET)"
	@echo "$(COLOR_DIM)  Run 'make up' to start the stack, or 'make check' to validate the repo$(COLOR_RESET)"

.PHONY: install-uv
install-uv: ## Install the uv Python package manager if missing
	@if ! command -v $(UV) >/dev/null 2>&1; then \
		echo "$(COLOR_BLUE)→$(COLOR_RESET) uv not found, installing..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	else \
		echo "$(COLOR_GREEN)✓$(COLOR_RESET) uv already installed"; \
	fi

.PHONY: install-backend
install-backend: install-uv ## Sync the backend virtualenv (apps/server/.venv)
	@echo "$(COLOR_BLUE)→$(COLOR_RESET) Syncing backend dependencies..."
	@cd $(SERVER_DIR) && $(UV) sync $(UV_GROUPS)
	@echo "$(COLOR_GREEN)✓$(COLOR_RESET) Backend dependencies synced"

.PHONY: install-frontend
install-frontend: ## Install frontend dependencies (apps/client)
	$(call _require,$(PNPM),See https://pnpm.io/installation)
	@echo "$(COLOR_BLUE)→$(COLOR_RESET) Installing frontend dependencies..."
	@$(PNPM) --dir $(CLIENT_DIR) install
	@echo "$(COLOR_GREEN)✓$(COLOR_RESET) Frontend dependencies installed"

.PHONY: install-hooks
install-hooks: ## Install git hooks (husky + pre-commit)
	$(call _require,$(PNPM),See https://pnpm.io/installation)
	@echo "$(COLOR_BLUE)→$(COLOR_RESET) Installing git hooks..."
	@$(PNPM) install
	@if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit install; \
	else \
		echo "$(COLOR_YELLOW)⚠$(COLOR_RESET) pre-commit not installed — Python hooks will be skipped."; \
		echo "$(COLOR_DIM)  Install it with: uv tool install pre-commit  (or pipx install pre-commit)$(COLOR_RESET)"; \
	fi
	@echo "$(COLOR_GREEN)✓$(COLOR_RESET) Git hooks installed"

.PHONY: install-system
install-system: ## Install system dependencies (poppler)
ifeq ($(shell uname), Linux)
	sudo apt update && sudo apt install -y poppler-utils
else ifeq ($(shell uname), Darwin)
	brew install poppler
else
	@echo "$(COLOR_YELLOW)⚠$(COLOR_RESET) Automatic install is not supported on this platform"
endif

# Backwards-compatible alias — `install-local` was the previous name.
.PHONY: install-local
install-local: install-system ## Alias for install-system (deprecated)

.PHONY: doctor
doctor: ## Report which required tools are present on this machine
	@echo ""
	@echo "$(COLOR_BOLD)  Toolchain$(COLOR_RESET)"
	@for tool in docker uv pnpm node python3 pre-commit kind; do \
		if command -v $$tool >/dev/null 2>&1; then \
			printf "  $(COLOR_GREEN)✓$(COLOR_RESET) %-12s %s\n" "$$tool" "$$($$tool --version 2>&1 | head -1)"; \
		else \
			printf "  $(COLOR_RED)✗$(COLOR_RESET) %-12s missing\n" "$$tool"; \
		fi; \
	done
	@echo ""

# -----------------------------------------------------------------------------
## ▸ Development
# -----------------------------------------------------------------------------

# `.env` is not tracked (see .gitignore): create it from the template when missing, so a
# fresh clone or a CI runner gets the local-stack defaults docker-compose expects.
.env:
	cp .env.example .env

.PHONY: up
up: .env ## Start the containerised development stack
	@$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) up -d

.PHONY: down
down: ## Stop the containerised development stack
	@$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) down || true

.PHONY: restart
restart: down up ## Restart the containerised development stack

.PHONY: ps
ps: ## Show the state of the development stack
	@$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) ps

.PHONY: dev-frontend
dev-frontend: ## Run the Vite dev server on the host (no container)
	@$(PNPM) --dir $(CLIENT_DIR) run dev

.PHONY: up-frontend
up-frontend: install-frontend ## Build and start the frontend container
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FRONT) build
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FRONT) up -d $(SVC_FRONTEND) --force-recreate

.PHONY: down-frontend
down-frontend: ## Stop the frontend container
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FRONT) down || true

.PHONY: logs
logs: ## Tail the logs of the whole development stack
	@$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) logs -f

.PHONY: logs-api
logs-api: ## Tail the API container logs
	@$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) logs -f $(SVC_BACKEND)

.PHONY: logs-service
logs-service: ## Tail the OCR service container logs
	@$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) logs -f $(SVC_SERVICE)

.PHONY: logs-frontend
logs-frontend: ## Tail the frontend container logs
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FRONT) logs -f $(SVC_FRONTEND)

.PHONY: shell-api
shell-api: ## Open a shell in the API container
	@$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) exec $(SVC_BACKEND) /bin/sh

.PHONY: generate-openapi
generate-openapi: up-frontend ## Regenerate the frontend OpenAPI types from the running API
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FRONT) exec $(SVC_FRONTEND) $(PNPM) run generate-openapi

# -----------------------------------------------------------------------------
## ▸ Quality
# -----------------------------------------------------------------------------

.PHONY: check
check: lint type-check test ## Run the full validation suite (lint + types + tests)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)  ✓ All checks passed$(COLOR_RESET)"

.PHONY: lint
lint: lint-backend lint-frontend ## Lint the whole repository

.PHONY: lint-backend
lint-backend: install-uv ## Lint the Python code (ruff check + format --check)
	@echo "$(COLOR_BLUE)→$(COLOR_RESET) Linting backend..."
	@cd $(SERVER_DIR) && \
		$(UV) run ruff check --exclude '**/*.ipynb' . && \
		$(UV) run ruff format --check .

.PHONY: lint-frontend
lint-frontend: ## Lint the frontend and repository-level files (eslint)
	@echo "$(COLOR_BLUE)→$(COLOR_RESET) Linting frontend..."
	@$(PNPM) --dir $(CLIENT_DIR) run lint
	@echo "$(COLOR_BLUE)→$(COLOR_RESET) Linting root files..."
	@$(PNPM) run lint:root

.PHONY: format
format: format-backend format-frontend ## Auto-fix lint and formatting issues everywhere

.PHONY: format-backend
format-backend: install-uv ## Auto-fix the Python code (ruff check --fix + format)
	@cd $(SERVER_DIR) && \
		$(UV) run ruff check --exclude '**/*.ipynb' . --fix && \
		$(UV) run ruff format .

.PHONY: format-frontend
format-frontend: ## Auto-fix the frontend and repository-level files (eslint --fix)
	@$(PNPM) --dir $(CLIENT_DIR) run format
	@$(PNPM) run format:root

# Backwards-compatible alias — `lint-fix` was the previous name.
.PHONY: lint-fix
lint-fix: format-backend ## Alias for format-backend (deprecated)

.PHONY: type-check
type-check: ## Type-check the frontend (vue-tsc)
	@echo "$(COLOR_BLUE)→$(COLOR_RESET) Type-checking frontend..."
	@$(PNPM) --dir $(CLIENT_DIR) run type-check

# -----------------------------------------------------------------------------
## ▸ Testing
# -----------------------------------------------------------------------------

.PHONY: test
test: tests test-frontend ## Run the backend and frontend unit tests

.PHONY: tests
tests: install-uv ## Run the backend unit tests (pytest, on the host)
	@cd $(SERVER_DIR) && $(UV) run pytest tests/ -v --tb=short

.PHONY: test-frontend
test-frontend: ## Run the frontend unit tests (vitest)
	@$(PNPM) --dir $(CLIENT_DIR) run test:unit

.PHONY: test-frontend-cov
test-frontend-cov: ## Run the frontend unit tests with coverage
	@$(PNPM) --dir $(CLIENT_DIR) run test:cov

.PHONY: test-e2e
test-e2e: ## Run the Playwright end-to-end tests
	@$(PNPM) --dir $(CLIENT_DIR) run test:e2e

.PHONY: test-e2e-ui
test-e2e-ui: ## Run the Playwright end-to-end tests in UI mode
	@$(PNPM) --dir $(CLIENT_DIR) run test:e2e:ui

.PHONY: test-e2e-install
test-e2e-install: ## Install the Playwright browsers
	@$(PNPM) --dir $(CLIENT_DIR) run test:e2e:install

.PHONY: test-backend-api
test-backend-api: build-deps up-db ## Run the backend API test suite in Docker
	@$(DOCKER_COMPOSE) -f $(COMPOSE_TEST) up $(SVC_BACKEND) --exit-code-from $(SVC_BACKEND)
	@$(MAKE) down-test

.PHONY: test-services-paddleocr2.10.0
test-services-paddleocr2.10.0: build-deps up-db ## Run the PaddleOCR 2.10.0 service tests
	@$(DOCKER_COMPOSE) -f $(COMPOSE_TEST) up paddleocr2_service --exit-code-from paddleocr2_service
	@$(MAKE) down-test

.PHONY: tests-liteparse
tests-liteparse: up-db ## Run the liteparse tests in Docker
	@$(DOCKER_COMPOSE) -f $(COMPOSE_TEST) -f $(COMPOSE_LITEPARSE) \
		up liteparse_service --no-build --exit-code-from liteparse_service
	@$(MAKE) down-test

.PHONY: test-sdk
test-sdk: .env install-uv ## Run the Python SDK test suite against a live stack
	@$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) up -d
	@cd $(SDK_DIR) && \
		$(UV) sync --dev && \
		$(UV) run pytest -s --cov=ocr_sdk --cov-report=term-missing -ra -v --maxfail=0 tests; \
		status=$$?; \
		$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) down -v; \
		exit $$status

.PHONY: stress-test
stress-test: install-uv ## Run a load test (locust)
	@cd $(SERVER_DIR) && $(UV) run locust -f stress-script/1-stress-test.py --host $(STRESS_HOST)

.PHONY: stress-stats
stress-stats: install-uv ## Print the load-test statistics
	@cd $(SERVER_DIR) && STRESS_HOST=$(STRESS_HOST) $(UV) run stress-script/2-process-stats.py

# -----------------------------------------------------------------------------
## ▸ Database
# -----------------------------------------------------------------------------

.PHONY: up-db
up-db: .env ## Start only the data services (db, rustfs, redis) and apply migrations
	@$(DOCKER_COMPOSE) -f $(COMPOSE_TEST) up -d db rustfs redis $(SVC_MIGRATION)

.PHONY: upgrade-db
upgrade-db: ## Apply the pending database migrations
	@$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) run --rm $(SVC_MIGRATION) alembic upgrade head

.PHONY: list-revision
list-revision: ## List the database revisions
	@$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) run --rm $(SVC_MIGRATION) alembic history

.PHONY: upgrade-revision
upgrade-revision: ## Create a new database revision (autogenerate)
	@read -p "Revision message: " msg; \
	$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) run --rm $(SVC_MIGRATION) alembic revision --autogenerate -m "$$msg"

.PHONY: stamp-db
stamp-db: ## Move the alembic pointer to a given revision
	@read -p "Revision id: " revision; \
	$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) run --rm $(SVC_MIGRATION) alembic stamp $$revision

# -----------------------------------------------------------------------------
## ▸ Docker images
# -----------------------------------------------------------------------------

.PHONY: build
build: build-ocr-backend build-ocr-service ## Build every backend Docker image

.PHONY: build-ocr-backend
build-ocr-backend: ## Build the backend Docker image
	@$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) build $(SVC_BACKEND)

.PHONY: build-ocr-service
build-ocr-service: ## Build the OCR service Docker image
	@$(DOCKER_COMPOSE) -f $(COMPOSE_DEV) build $(SVC_SERVICE)

.PHONY: build-ocr-frontend
build-ocr-frontend: ## Build the frontend Docker image
	@$(DOCKER_COMPOSE) -f $(COMPOSE_FRONT) build $(SVC_FRONTEND)

.PHONY: build-deps
build-deps: .env ## Build the Docker images the test stack depends on
	@$(DOCKER_COMPOSE) -f $(COMPOSE_TEST) build rustfs redis db $(SVC_MIGRATION)

# Backwards-compatible alias — `build-container-dependencies` was the previous name.
.PHONY: build-container-dependencies
build-container-dependencies: build-deps ## Alias for build-deps (deprecated)

.PHONY: build-liteparse
build-liteparse: ## Build the liteparse Docker image (required on first run)
	@$(DOCKER_COMPOSE) -f $(COMPOSE_TEST) -f $(COMPOSE_LITEPARSE) build liteparse_service

# -----------------------------------------------------------------------------
## ▸ Kubernetes (kind)
# -----------------------------------------------------------------------------

.PHONY: cluster
cluster: ## Create a local kind cluster
	$(call _require,kind,See https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
	@kind create cluster --name ocr --config ./kind/config.yaml

.PHONY: cluster-delete
cluster-delete: ## Delete the local kind cluster
	@kind delete cluster --name ocr || true

.PHONY: load-image
load-image: ## Load the locally built images into the kind cluster
	@docker image tag ocr-api:latest ocr-api:v1
	@docker image tag ocr-worker:latest ocr-worker:v1
	@kind load docker-image ocr-worker:v1 ocr-api:v1 --name ocr

# -----------------------------------------------------------------------------
## ▸ Release
# -----------------------------------------------------------------------------

.PHONY: bump-patch
bump-patch: ## Bump the patch version (commitizen)
	@cd $(SERVER_DIR) && $(UV) run cz bump --increment patch

.PHONY: bump-minor
bump-minor: ## Bump the minor version (commitizen)
	@cd $(SERVER_DIR) && $(UV) run cz bump --increment minor

# -----------------------------------------------------------------------------
## ▸ Cleanup
# -----------------------------------------------------------------------------

.PHONY: down-test
down-test: ## Stop the test stack and remove orphans/volumes
	@$(DOCKER_COMPOSE) -f $(COMPOSE_TEST) down --remove-orphans -v || true

.PHONY: clean
clean: down down-test clean-frontend ## Remove caches, build artefacts and containers
	@rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache
	@rm -rf $(SERVER_DIR)/.ruff_cache $(SERVER_DIR)/.pytest_cache
	@echo "$(COLOR_GREEN)✓$(COLOR_RESET) Workspace cleaned"

.PHONY: clean-frontend
clean-frontend: down-frontend ## Remove the frontend build artefacts and node_modules
	@# node_modules can be root-owned when it was created from inside a container.
	@if [ -d "$(CLIENT_DIR)/node_modules" ] && [ "$$(stat -f %Su $(CLIENT_DIR)/node_modules 2>/dev/null || stat -c %U $(CLIENT_DIR)/node_modules 2>/dev/null || echo unknown)" != "$$(whoami)" ]; then \
		echo "$(COLOR_YELLOW)⚠$(COLOR_RESET) node_modules is not owned by $$(whoami), fixing permissions..."; \
		sudo chown -R $$(id -u):$$(id -g) $(CLIENT_DIR)/node_modules || true; \
	fi
	@rm -rf $(CLIENT_DIR)/node_modules $(CLIENT_DIR)/dist $(CLIENT_DIR)/.nuxt $(CLIENT_DIR)/.output
	@echo "$(COLOR_GREEN)✓$(COLOR_RESET) Frontend cleaned"

# Backwards-compatible alias — `clean-front` was the previous name.
.PHONY: clean-front
clean-front: clean-frontend ## Alias for clean-frontend (deprecated)
