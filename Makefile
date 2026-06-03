.PHONY: install dev test coverage lint format clean build

install:
	pip install -e .
	python -m spacy download en_core_web_sm

dev:
	pip install -e ".[dev,all]"
	python -m spacy download en_core_web_sm

test:
	pytest tests/ -v

coverage:
	pytest tests/ -v --cov=redactify --cov-report=html --cov-report=term
	@echo "\n  HTML report: htmlcov/index.html"

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +

build:
	python -m build
