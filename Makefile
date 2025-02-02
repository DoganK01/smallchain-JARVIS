.PHONY: install install-dev format lint test security clean run serve-docs

PROJECT := smallchain
VENV := .venv
PYTHON := poetry run
APP_RAG := app_rag.py
APP_TOOLS := app_tools.py

install:
    poetry install --no-root

install-dev:
    poetry install --with dev

format:
    $(PYTHON) isort .
    $(PYTHON) black .
    $(PYTHON) autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place . --exclude=__init__.py

lint:
    $(PYTHON) pylint --rcfile=pylint.yaml $(PROJECT) app_*.py
    $(PYTHON) flake8 .
    $(PYTHON) mypy .

test:
    $(PYTHON) pytest -v --cov=$(PROJECT) --cov-report=html --cov-report=xml --cov-config=pyproject.toml

security:
    $(PYTHON) safety check --full-report
    $(PYTHON) bandit -r $(PROJECT)

clean:
    rm -rf .coverage coverage.xml htmlcov .pytest_cache .mypy_cache
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

run:
    @echo "Available applications:"
    @echo "1. RAG Application (app_rag.py)"
    @echo "2. Tools Application (app_tools.py)"
    @read -p "Enter choice (1/2): " choice; \
    case $$choice in \
        1) $(PYTHON) python $(APP_RAG) ;; \
        2) $(PYTHON) python $(APP_TOOLS) ;; \
        *) echo "Invalid choice"; exit 1 ;; \
    esac

serve-docs:
    $(PYTHON) mkdocs serve
