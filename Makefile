<<<<<<< HEAD
# Define variables
PYTHON = python
POETRY = poetry
SRC = src
APP = $(SRC)/app.py

# Default goal
.DEFAULT_GOAL := help

# Help: List all tasks
help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Install dependencies
install: ## Install all dependencies using Poetry
	$(POETRY) install

# Update dependencies
update: ## Update all dependencies using Poetry
	$(POETRY) update

# Run the application
run: ## Run the main application
	$(POETRY) run $(PYTHON) $(APP)

# Format the code
format: ## Format the code with Black
	$(POETRY) run black $(SRC)

# Lint the code
lint: ## Lint the code with Flake8
	$(POETRY) run flake8 $(SRC)

# Run tests
test: ## Run tests using Pytest
	$(POETRY) run pytest

# Clean temporary files
clean: ## Clean up temporary files
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

# Build the project
build: ## Build the project using Poetry
	$(POETRY) build


# Shell
shell: ## Open a Python interactive shell

	$(POETRY) run $(PYTHON)
=======
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
>>>>>>> 8408410155300391741746111fec68794621c62e
