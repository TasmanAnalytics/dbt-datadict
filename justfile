set dotenv-load

[doc("Sync uv dependencies.")]
ensure-uv:
	uv sync --all-groups

[doc("Install pre-commit hooks.")]
ensure-pre-commit:
	uv run pre-commit install -f --install-hooks

[doc("Ensure uv dependencies and pre-commit hooks are setup.")]
ensure-uv-and-pre-commit: ensure-uv ensure-pre-commit

[doc("Publish the datadict Python package to Test PyPI.")]
publish-test: build
	uv publish --index testpypi

[doc("Publish the datadict Python package to PyPI.")]
publish: build
	uv publish --token "$PYPI_TOKEN"

[doc("Build the datadict Python package")]
build:
	rm -rf dist/ && uv build

[doc("Build and serve the Python docs for this repo.")]
docs:
	uv sync --group docs
	uv run mkdocs build
	uv run mkdocs serve

[doc("Deploy documentation to GitHub Pages.")]
docs-deploy:
	uv sync --group docs
	uv run mkdocs gh-deploy --force

[doc("Run tests for datadict.

This will run tests with the `-v` flag.
")]
test:
	uv sync --group test
	uv run pytest -v

[doc("Run linting for datadict.

This will run all the pre-commit checks.
")]
lint:
	@echo "\\033[0;34mpre-commit checks\\033[0m"
	SKIP=identity pre-commit run --all-files --hook-stage pre-commit
	@echo "\\033[0;34mpre-push checks\\033[0m"
	SKIP=identity pre-commit run --all-files --hook-stage pre-push

[doc("Clean environment.

Remove pre-commit hooks and uv virtual environment.
")]
clean:
	pre-commit uninstall
	@echo Uninstalling the uv virtual environment.
	rm -rf .venv
