install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync && npm --prefix frontend install

dev:
	make dev-backend & make dev-frontend

dev-backend:
	uv run python run_integrated_server.py

dev-frontend:
	npm --prefix frontend run dev

test:
	uv run pytest

test-coverage:
	uv run pytest --cov=app --cov-report=html --cov-report=term

lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy .

format:
	uv run ruff format .
	uv run ruff check . --fix

clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test-integration:
	uv run python test_integration.py

deploy-backend:
	@chmod +x deploy.sh
	./deploy.sh backend

deploy-frontend:
	@chmod +x deploy.sh
	./deploy.sh frontend

deploy:
	@chmod +x deploy.sh
	./deploy.sh both

.PHONY: install dev dev-backend dev-frontend test test-integration test-coverage lint format clean deploy deploy-backend deploy-frontend
