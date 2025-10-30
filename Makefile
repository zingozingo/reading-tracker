.PHONY: help install start stop restart backend frontend frontend-status restart-frontend logs clean test db-setup db-check kill-all git-status git-commit hooks-install hooks-uninstall hooks-test

# Color codes for better readability
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Project configuration
VENV := venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn
BACKEND_PORT := 8000
FRONTEND_PORT := 3000

help: ## Show this help message
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  BookTracker API - Available Commands$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)Quick Start:$(NC) make install && make start"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo ""

# ============================================================
# Installation & Setup
# ============================================================

install: ## Install all dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(YELLOW)Creating virtual environment...$(NC)"; \
		python3 -m venv $(VENV); \
	fi
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed successfully!$(NC)"

venv: ## Create virtual environment
	@echo "$(GREEN)Creating virtual environment...$(NC)"
	python3 -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created!$(NC)"
	@echo "$(YELLOW)Run 'source $(VENV)/bin/activate' to activate$(NC)"

clean-venv: ## Remove virtual environment
	@echo "$(RED)Removing virtual environment...$(NC)"
	rm -rf $(VENV)
	@echo "$(GREEN)✓ Virtual environment removed$(NC)"

requirements: ## Update requirements.txt with current packages
	@echo "$(GREEN)Updating requirements.txt...$(NC)"
	@$(PIP) freeze > requirements.txt
	@echo "$(GREEN)✓ requirements.txt updated$(NC)"

# ============================================================
# Server Management
# ============================================================

kill-all: ## Forcefully kill all processes (daemon + ports 3000/8000)
	@echo "$(YELLOW)Forcefully killing all processes...$(NC)"
	@# Stop daemon first
	@-$(PYTHON) scripts/frontend_manager.py stop 2>/dev/null || true
	@# Kill any remaining processes on ports
	@-pids=$$(lsof -ti:$(BACKEND_PORT),$(FRONTEND_PORT) 2>/dev/null); \
	if [ -n "$$pids" ]; then \
		echo "  $(YELLOW)Found processes on ports: $$pids$(NC)"; \
		echo $$pids | xargs kill -9 2>/dev/null && echo "  $(GREEN)✓ Port processes killed$(NC)" || true; \
	else \
		echo "  $(GREEN)✓ No processes found on ports$(NC)"; \
	fi
	@sleep 1

start: kill-all db-check ## Start both frontend and backend servers (kills old processes first)
	@echo ""
	@echo "$(GREEN)Starting BookTracker servers...$(NC)"
	@echo ""
	@$(MAKE) backend
	@echo ""
	@$(MAKE) frontend
	@echo ""
	@echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  ✓ BookTracker is running!$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Frontend:$(NC) http://localhost:$(FRONTEND_PORT)"
	@echo "$(YELLOW)Backend:$(NC)  http://localhost:$(BACKEND_PORT)"
	@echo "$(YELLOW)API Docs:$(NC) http://localhost:$(BACKEND_PORT)/docs"
	@echo ""
	@echo "$(BLUE)Tip: Run 'make logs' to view server logs$(NC)"
	@echo "$(BLUE)Tip: Run 'make stop' to stop all servers$(NC)"
	@echo ""

backend: db-check ## Start backend server in background (daemon mode)
	@echo "$(GREEN)Starting backend server on port $(BACKEND_PORT)...$(NC)"
	@mkdir -p logs
	@nohup $(UVICORN) main:app --reload --host 0.0.0.0 --port $(BACKEND_PORT) \
		> logs/backend.log 2> logs/backend_error.log & \
		echo $$! > logs/backend.pid
	@sleep 1
	@if lsof -ti:$(BACKEND_PORT) > /dev/null 2>&1; then \
		echo "$(GREEN)✓ Backend started successfully (PID: $$(cat logs/backend.pid))$(NC)"; \
		echo "  Logs: logs/backend.log"; \
		echo "  Errors: logs/backend_error.log"; \
	else \
		echo "$(RED)✗ Backend failed to start. Check logs/backend_error.log$(NC)"; \
		exit 1; \
	fi

frontend: ## Start frontend server as daemon (background)
	@$(PYTHON) scripts/frontend_manager.py start

stop: ## Stop all running servers
	@echo "$(YELLOW)Stopping all servers...$(NC)"
	@$(MAKE) stop-backend
	@$(MAKE) stop-frontend
	@echo "$(GREEN)✓ All servers stopped$(NC)"

restart: stop start ## Restart all servers

stop-backend: ## Stop backend server only
	@if [ -f logs/backend.pid ]; then \
		PID=$$(cat logs/backend.pid); \
		if ps -p $$PID > /dev/null 2>&1; then \
			echo "$(YELLOW)Stopping backend server (PID: $$PID)...$(NC)"; \
			kill $$PID 2>/dev/null || kill -9 $$PID 2>/dev/null || true; \
			rm -f logs/backend.pid; \
			echo "$(GREEN)✓ Backend stopped$(NC)"; \
		else \
			echo "$(YELLOW)Backend not running (stale PID)$(NC)"; \
			rm -f logs/backend.pid; \
		fi \
	else \
		echo "$(YELLOW)Backend not running (no PID file)$(NC)"; \
	fi
	@-lsof -ti:$(BACKEND_PORT) | xargs kill -9 2>/dev/null || true

stop-frontend: ## Stop frontend daemon
	@$(PYTHON) scripts/frontend_manager.py stop

status: ## Check server status
	@echo "$(BLUE)Checking server status...$(NC)"
	@echo ""
	@echo "$(YELLOW)Backend (port $(BACKEND_PORT)):$(NC)"
	@if [ -f logs/backend.pid ]; then \
		PID=$$(cat logs/backend.pid); \
		if ps -p $$PID > /dev/null 2>&1; then \
			echo "  $(GREEN)✓ Running (PID: $$PID)$(NC)"; \
		else \
			echo "  $(RED)✗ Not running (stale PID)$(NC)"; \
		fi \
	else \
		if lsof -ti:$(BACKEND_PORT) > /dev/null 2>&1; then \
			echo "  $(YELLOW)⚠ Running but no PID file$(NC)"; \
		else \
			echo "  $(RED)✗ Not running$(NC)"; \
		fi \
	fi
	@echo ""
	@echo "$(YELLOW)Frontend Daemon:$(NC)"
	@-$(PYTHON) scripts/frontend_manager.py status 2>/dev/null | grep -A1 "Status:" | tail -1 || echo "  $(RED)✗ Not running$(NC)"
	@echo ""

frontend-status: ## Show detailed frontend daemon status
	@$(PYTHON) scripts/frontend_manager.py status

restart-frontend: ## Restart frontend daemon
	@$(PYTHON) scripts/frontend_manager.py restart

# ============================================================
# Database Operations
# ============================================================

db-check: ## Check if database is accessible
	@echo "$(BLUE)Checking database connection...$(NC)"
	@$(PYTHON) scripts/check_db.py || exit 1

db-setup: ## Setup database (requires MySQL running)
	@echo "$(GREEN)Setting up database...$(NC)"
	@$(PYTHON) -c "from app.core.database import engine, Base; from app.models import book, reading_session; Base.metadata.create_all(bind=engine); print('✓ Database tables created!')"

db-reset: ## Drop and recreate all database tables (DESTRUCTIVE!)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(PYTHON) -c "from app.core.database import engine, Base; from app.models import book, reading_session; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine); print('✓ Database reset complete!')"; \
	else \
		echo "$(YELLOW)Database reset cancelled$(NC)"; \
	fi

# ============================================================
# Logging & Monitoring
# ============================================================

logs: ## View all server logs (Ctrl+C to exit)
	@echo "$(BLUE)Viewing all server logs (Ctrl+C to exit)...$(NC)"
	@tail -f logs/backend.log logs/frontend.log 2>/dev/null || echo "$(YELLOW)No log files found. Servers may not be running.$(NC)"

logs-backend: ## View backend logs only
	@echo "$(BLUE)Viewing backend logs...$(NC)"
	@tail -f logs/backend.log 2>/dev/null || echo "$(YELLOW)Backend log not found$(NC)"

logs-backend-error: ## View backend error logs
	@echo "$(BLUE)Viewing backend error logs...$(NC)"
	@tail -f logs/backend_error.log 2>/dev/null || echo "$(YELLOW)Backend error log not found$(NC)"

logs-frontend: ## View frontend logs only
	@echo "$(BLUE)Viewing frontend logs...$(NC)"
	@tail -f logs/frontend.log 2>/dev/null || echo "$(YELLOW)Frontend log not found$(NC)"

logs-frontend-error: ## View frontend error logs
	@echo "$(BLUE)Viewing frontend error logs...$(NC)"
	@tail -f logs/frontend_error.log 2>/dev/null || echo "$(YELLOW)Frontend error log not found$(NC)"

logs-all: ## View all logs (backend + frontend, normal + error)
	@echo "$(BLUE)Viewing all logs (Ctrl+C to exit)...$(NC)"
	@tail -f logs/backend.log logs/backend_error.log logs/frontend.log logs/frontend_error.log 2>/dev/null || echo "$(YELLOW)No log files found$(NC)"

# ============================================================
# Testing & Quality
# ============================================================

test: ## Run all tests with pytest
	@echo "$(GREEN)Running tests...$(NC)"
	@echo ""
	@$(PYTHON) -m pytest tests/ -v --tb=short
	@echo ""

test-verbose: ## Run tests with detailed output
	@echo "$(GREEN)Running tests with verbose output...$(NC)"
	@$(PYTHON) -m pytest tests/ -vv --tb=long

test-coverage: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	@$(PYTHON) -m pytest tests/ --cov=app --cov-report=term-missing || echo "$(RED)pytest-cov not installed. Run: pip install pytest-cov$(NC)"

test-quick: ## Run tests without verbose output
	@$(PYTHON) -m pytest tests/ --tb=short -q

lint: ## Run linting checks
	@echo "$(YELLOW)Running linting...$(NC)"
	@$(PYTHON) -m flake8 app/ --max-line-length=120 2>/dev/null || echo "$(RED)flake8 not installed. Run: pip install flake8$(NC)"

format: ## Format code with black
	@echo "$(YELLOW)Formatting code...$(NC)"
	@$(PYTHON) -m black app/ main.py 2>/dev/null || echo "$(RED)black not installed. Run: pip install black$(NC)"

# ============================================================
# Git Operations
# ============================================================

git-status: ## Show git status
	@git status

git-log: ## Show recent git commits
	@git log --oneline -10

git-branch: ## Show current branch
	@git branch --show-current

git-commit: ## Quick commit (usage: make git-commit m="your message")
	@if [ -z "$(m)" ]; then \
		echo "$(RED)Error: Please provide a commit message$(NC)"; \
		echo "Usage: make git-commit m=\"your message\""; \
		exit 1; \
	fi
	@git add .
	@git commit -m "$(m)"
	@echo "$(GREEN)✓ Changes committed$(NC)"

git-push: ## Push to remote
	@echo "$(YELLOW)Pushing to remote...$(NC)"
	@git push
	@echo "$(GREEN)✓ Pushed successfully$(NC)"

hooks-install: ## Install git pre-commit hooks
	@echo "$(GREEN)Installing git hooks...$(NC)"
	@if [ -f .git/hooks/pre-commit ]; then \
		echo "$(YELLOW)Backing up existing pre-commit hook...$(NC)"; \
		mv .git/hooks/pre-commit .git/hooks/pre-commit.backup; \
		echo "  Saved to: .git/hooks/pre-commit.backup"; \
	fi
	@cp scripts/pre-commit .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "$(GREEN)✓ Pre-commit hook installed successfully$(NC)"
	@echo ""
	@echo "$(BLUE)The hook will run automatically on 'git commit'$(NC)"
	@echo "$(BLUE)To bypass: git commit --no-verify$(NC)"

hooks-uninstall: ## Uninstall git pre-commit hooks
	@echo "$(YELLOW)Uninstalling git hooks...$(NC)"
	@if [ -f .git/hooks/pre-commit ]; then \
		rm .git/hooks/pre-commit; \
		echo "$(GREEN)✓ Pre-commit hook removed$(NC)"; \
		if [ -f .git/hooks/pre-commit.backup ]; then \
			echo "$(BLUE)Backup exists at: .git/hooks/pre-commit.backup$(NC)"; \
		fi \
	else \
		echo "$(YELLOW)No pre-commit hook installed$(NC)"; \
	fi

hooks-test: ## Test pre-commit hook without committing
	@echo "$(BLUE)Testing pre-commit hook...$(NC)"
	@echo ""
	@if [ -f .git/hooks/pre-commit ]; then \
		.git/hooks/pre-commit; \
	else \
		echo "$(RED)✗ Pre-commit hook not installed$(NC)"; \
		echo "$(YELLOW)Run: make hooks-install$(NC)"; \
	fi

# ============================================================
# Cleanup
# ============================================================

clean: ## Clean up temporary files and caches
	@echo "$(YELLOW)Cleaning up...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf logs/*.log logs/*.pid 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: clean clean-venv ## Clean everything including virtual environment
	@echo "$(GREEN)✓ Full cleanup complete$(NC)"

# ============================================================
# Development Helpers
# ============================================================

dev: db-check ## Start development environment (backend only, auto-reload)
	@echo "$(GREEN)Starting development mode...$(NC)"
	@$(UVICORN) main:app --reload --host 0.0.0.0 --port $(BACKEND_PORT)

shell: ## Open Python shell with app context
	@echo "$(BLUE)Opening Python shell...$(NC)"
	@$(PYTHON) -i -c "from app.core.database import SessionLocal, engine; from app.models import book, reading_session; from app import crud, schemas; db = SessionLocal(); print('Database session available as: db'); print('Models: book, reading_session'); print('Modules: crud, schemas')"

check-ports: ## Check if ports are available
	@echo "$(BLUE)Checking ports...$(NC)"
	@echo ""
	@echo "$(YELLOW)Port $(BACKEND_PORT) (Backend):$(NC)"
	@lsof -ti:$(BACKEND_PORT) > /dev/null 2>&1 && echo "  $(RED)✗ In use$(NC)" || echo "  $(GREEN)✓ Available$(NC)"
	@echo ""
	@echo "$(YELLOW)Port $(FRONTEND_PORT) (Frontend):$(NC)"
	@lsof -ti:$(FRONTEND_PORT) > /dev/null 2>&1 && echo "  $(RED)✗ In use$(NC)" || echo "  $(GREEN)✓ Available$(NC)"
	@echo ""

info: ## Show project information
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  BookTracker API - Project Information$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Project Name:$(NC)     BookTracker API"
	@echo "$(YELLOW)Version:$(NC)         1.0.0"
	@echo "$(YELLOW)Python:$(NC)          $$($(PYTHON) --version 2>&1)"
	@echo "$(YELLOW)Backend Port:$(NC)    $(BACKEND_PORT)"
	@echo "$(YELLOW)Frontend Port:$(NC)   $(FRONTEND_PORT)"
	@echo "$(YELLOW)Git Branch:$(NC)      $$(git branch --show-current)"
	@echo "$(YELLOW)Virtual Env:$(NC)     $(VENV)"
	@if [ -f .git/hooks/pre-commit ]; then \
		echo "$(YELLOW)Git Hooks:$(NC)       $(GREEN)✓ Installed$(NC)"; \
	else \
		echo "$(YELLOW)Git Hooks:$(NC)       $(RED)✗ Not installed$(NC) (run: make hooks-install)"; \
	fi
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo ""
