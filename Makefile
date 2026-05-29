.PHONY: install install-dev lint format typecheck test test-cov run-forge run-dashboard clean setup precommit

# ── Installation ──────────────────────────────────────────────

install:
	pip install -e ".[forge]"

install-dev:
	pip install -e ".[forge,dev]"
	pre-commit install

setup: install-dev
	cp -n .env.example .env 2>/dev/null || true
	echo "✓ Setup complete. Edit .env to configure your LLM provider."

# ── Quality ───────────────────────────────────────────────────

lint:
	ruff check agent_forge/ dashboard/ tests/ --statistics

format:
	ruff format agent_forge/ dashboard/ tests/

typecheck:
	mypy agent_forge/ --ignore-missing-imports --python-version=3.12

# ── Testing ───────────────────────────────────────────────────

test:
	python -m pytest tests/ -v --tb=short

test-cov:
	python -m pytest tests/ -v --tb=short --cov=agent_forge --cov-report=term-missing

test-watch:
	python -m pytest tests/ -f  # fail-fast, re-run on changes

# ── Run ───────────────────────────────────────────────────────

run-forge:
	python -m agent_forge

run-forge-cycles:
	python -m agent_forge --cycles $(or ${CYCLES}, 10)

run-dashboard:
	uvicorn dashboard.main:app --reload --port ${DASHBOARD_PORT:-8000}

# ── Maintenance ───────────────────────────────────────────────

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache
	rm -rf *.egg-info dist build
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

precommit:
	pre-commit run --all-files

help:
	@echo "Grounded Agent Forge — Make targets:"
	@echo "  install         Install forge dependencies"
	@echo "  install-dev     Install forge + dev dependencies + pre-commit"
	@echo "  setup           Full dev setup (install-dev + .env)"
	@echo "  lint            Run ruff lint"
	@echo "  format          Run ruff formatter"
	@echo "  typecheck       Run mypy type checking"
	@echo "  test            Run tests (short output)"
	@echo "  test-cov        Run tests with coverage report"
	@echo "  run-forge       Start evolution loop"
	@echo "  run-dashboard   Start dashboard server"
	@echo "  clean           Remove caches and build artifacts"
	@echo "  precommit       Run all pre-commit hooks"
