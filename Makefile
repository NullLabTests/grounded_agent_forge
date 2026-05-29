.PHONY: install lint clean run-forge run-dashboard format

install:
	pip install -e ".[forge]"

lint:
	ruff check agent_forge/ dashboard/ --statistics

format:
	ruff format agent_forge/ dashboard/

run-forge:
	python -m agent_forge.orchestrator

run-dashboard:
	uvicorn dashboard.main:app --reload --port ${DASHBOARD_PORT:-8000}

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache
	rm -rf *.egg-info dist build
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
