.PHONY: install lint format typecheck test test-cov build clean

install:
	poetry install

lint:
	poetry run ruff check .
	poetry run ruff format --check .

format:
	poetry run ruff check --fix .
	poetry run ruff format .

typecheck:
	poetry run mypy src

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=pagotic --cov-report=term-missing

build:
	poetry build

clean:
	rm -rf build dist htmlcov .coverage coverage.xml .pytest_cache .ruff_cache .mypy_cache
