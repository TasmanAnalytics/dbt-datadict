#!/make
.PHONY: clean poetry
.DEFAULT_GOAL := help

poetry: ## Install poetry
	@if ! command -v poetry; then\
		curl -sSL https://install.python-poetry.org | python3 -;\
	fi
	poetry install

publish-test: build ##& Publish the datadict Python package to Test PyPI
	poetry publish --repository testpypi

build: poetry ## Build the datadict Python package
	poetry build

clean: ## Uninstall the dbt virtual environment
	@echo Uninstalling the Poetry virtual environment.
	poetry env remove python || rm -rf .venv

help:	## Show targets and comments (must have ##)
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
