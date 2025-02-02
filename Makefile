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
