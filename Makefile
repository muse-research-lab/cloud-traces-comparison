.PHONY : format lint test

format:
	python3 -m isort gtd/ tests/
	python3 -m black --target-version py38 gtd tests

lint:
	python3 -m mypy gtd/
	python3 -m isort gtd/ tests/ --check-only
	python3 -m flake8 gtd/ tests/
	python3 -m black --check gtd/ tests/

test:
	python3 -m pytest -n 8 tests/

coverage:
	python3 -m pytest -n 8 --cov=gtd tests/