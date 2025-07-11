#!/make
.PHONY: clean uv
.DEFAULT_GOAL := help

uv: ## Install uv
	@if ! command -v uv; then\
		curl -LsSf https://astral.sh/uv/install.sh | sh;\
	fi
	uv sync --all-groups

publish-test: build ##& Publish the datadict Python package to Test PyPI
	uv publish --index testpypi

build: uv ## Build the datadict Python package
	rm -rf dist/ && uv build

clean: ## Uninstall the dbt virtual environment
	@echo Uninstalling the uv virtual environment.
	rm -rf .venv

help: ## Show targets and comments (must have ##)
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
