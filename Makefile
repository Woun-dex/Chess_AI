.PHONY: help dev build test lint format check down clean

help:
	@echo "Available commands:"
	@echo "  make dev          Start PostgreSQL, Redis, Backend, and Frontend via Docker Compose"
	@echo "  make down         Stop all Docker Compose services"
	@echo "  make test         Run backend unit tests"
	@echo "  make lint         Run Ruff linter and MyPy type checker"
	@echo "  make check        Run backend tests, linting, and frontend TypeScript build"
	@echo "  make format       Auto-format backend code with Ruff"
	@echo "  make clean        Remove virtualenvs, pycache, and build artifacts"

dev:
	docker compose up --build

down:
	docker compose down

test:
	cd backend && .venv/bin/pytest tests/

lint:
	cd backend && .venv/bin/ruff check .
	cd backend && .venv/bin/mypy src/

check: lint test
	cd frontend && npm run build

format:
	cd backend && .venv/bin/ruff format .
	cd backend && .venv/bin/ruff check --fix .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf backend/.venv frontend/node_modules frontend/dist
