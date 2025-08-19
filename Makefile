#!/make
.PHONY: clean uv
.DEFAULT_GOAL := help

uv: ## Install uv
	@if ! command -v uv; then\
		curl -LsSf https://astral.sh/uv/install.sh | sh;\
	fi
	uv sync --all-groups
	pre-commit install --install-hooks

publish-test: build ##& Publish the datadict Python package to Test PyPI
	uv publish --index testpypi

build: uv ## Build the datadict Python package
	rm -rf dist/ && uv build

docs: uv ## Build the datadict Python package
	mkdocs build
	mkdocs serve

test: uv ## Test the datadict Python package
	uv run pytest -v

lint: uv ## Lint the datadict Python package
	@echo "\\033[0;34mpre-commit checks\\033[0m"
	SKIP=identity pre-commit run --all-files --hook-stage pre-commit
	@echo "\\033[0;34mpre-push checks\\033[0m"
	pre-commit run --all-files --hook-stage pre-push

clean: ## Uninstall the dbt virtual environment
	pre-commit uninstall
	@echo Uninstalling the uv virtual environment.
	rm -rf .venv

help: ## Show targets and comments (must have ##)
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
