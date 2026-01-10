# Compass Automation Makefile
# 
# Common commands for setting up and running the Compass automation project.
# 
# Usage:
#   make setup          - Full environment setup
#   make install        - Install dependencies only
#   make test           - Run tests
#   make run            - Run standalone automation
#   make clean          - Clean up generated files
#   make help           - Show this help

# Variables
PYTHON = python
VENV_DIR = venv
PIP = $(VENV_DIR)/Scripts/pip
PYTHON_VENV = $(VENV_DIR)/Scripts/python
ACTIVATE = $(VENV_DIR)/Scripts/Activate.ps1

# Default target
.DEFAULT_GOAL := help

# Setup everything
.PHONY: setup
setup: venv install config test-basic  ## Full environment setup
	@echo "Setup complete! Run 'make activate' to activate the environment."

# Create virtual environment
.PHONY: venv
venv:  ## Create virtual environment
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)

# Install dependencies
.PHONY: install
install: venv  ## Install dependencies
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install selenium>=4.0.0 pytest>=7.0.0 pytest-html

# Install development dependencies
.PHONY: install-dev
install-dev: install  ## Install development dependencies
	@echo "Installing development dependencies..."
	$(PIP) install flake8 black isort

# Create config files
.PHONY: config
config:  ## Create sample configuration files
	@echo "Creating sample configuration files..."
	@if not exist config mkdir config
	@if not exist data mkdir data
	@$(PYTHON_VENV) setup.py

# Run basic tests
.PHONY: test-basic
test-basic:  ## Run basic environment tests
	@echo "Running basic tests..."
	@$(PYTHON_VENV) -c "import selenium, pytest; print('✓ Basic imports successful')"

# Run full test suite
.PHONY: test
test:  ## Run full test suite
	@echo "Running full test suite..."
	$(PYTHON_VENV) -m pytest -v tests/

# Run smoke tests only
.PHONY: test-smoke
test-smoke:  ## Run smoke tests only
	@echo "Running smoke tests..."
	$(PYTHON_VENV) -m pytest -v -m smoke tests/

# Run standalone automation
.PHONY: run
run:  ## Run standalone automation
	@echo "Running Compass automation..."
	$(PYTHON_VENV) run_compass.py

# Format code
.PHONY: format
format:  ## Format code with black and isort
	@echo "Formatting code..."
	$(PYTHON_VENV) -m black .
	$(PYTHON_VENV) -m isort .

# Lint code
.PHONY: lint
lint:  ## Lint code with flake8
	@echo "Linting code..."
	$(PYTHON_VENV) -m flake8 .

# Generate requirements.txt
.PHONY: requirements
requirements:  ## Generate requirements.txt
	@echo "Generating requirements.txt..."
	$(PIP) freeze > requirements.txt

# Clean up
.PHONY: clean
clean:  ## Clean up generated files
	@echo "Cleaning up..."
	@if exist __pycache__ rmdir /s /q __pycache__
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist *.pyc del /q *.pyc
	@if exist *.log del /q *.log

# Clean everything including venv
.PHONY: clean-all
clean-all: clean  ## Clean everything including virtual environment
	@echo "Removing virtual environment..."
	@if exist $(VENV_DIR) rmdir /s /q $(VENV_DIR)

# Show activation command
.PHONY: activate
activate:  ## Show command to activate virtual environment
	@echo "To activate the virtual environment, run:"
	@echo "    .\$(ACTIVATE)"

# Check environment
.PHONY: check
check:  ## Check environment setup
	@echo "Checking environment..."
	@echo "Python version:"
	@$(PYTHON) --version
	@echo "Virtual environment:"
	@if exist $(VENV_DIR) echo "✓ Virtual environment exists" else echo "✗ Virtual environment missing"
	@echo "Dependencies:"
	@if exist $(VENV_DIR) $(PIP) list else echo "✗ Virtual environment not found"

# Help
.PHONY: help
help:  ## Show this help
	@echo "Compass Automation Makefile"
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  %-15s %s\n", $$1, $$2 } /^##@/ { printf "\n%s\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""
	@echo "Common workflows:"
	@echo "  1. Initial setup:    make setup"
	@echo "  2. Activate env:     make activate"
	@echo "  3. Run tests:        make test"
	@echo "  4. Run automation:   make run"