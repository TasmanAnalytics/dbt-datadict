# Developer guide

## Configuring a local environment

This is a Python project which uses [uv](https://github.com/astral-sh/uv) for package management.

After [installing uv](https://docs.astral.sh/uv/getting-started/installation/), create a virtual environment with the project's dependencies:

```shell
uv sync --all-groups
```

The [Makefile](../Makefile) has several commands to help with development tasks, such as:

```shell
make uv     # Install uv and sync dependencies
make build  # Build the package locally
make test   # Run the tests
```

If you're using a system without `make`, you can run the equivalent commands directly:

```shell
# Install uv and sync dependencies (Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | more"
uv sync --all-groups

# Build the package locally
uv build

# Run the tests
uv run pytest -v
```

## Publishing a new release

To publish a new release of the package to PyPI, you'll need to increment the project version and create a new release on GitHub.

### Incrementing the version

Update the version in the [`pyproject.toml`](../pyproject.toml) file, where the version specified is in line with the [PyPA Version Specifiers specification](https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers). You can either manually update the version or use `uv` commands:

```shell
uv version <version>

# or
uv version --bump <bump>  # `patch`, `minor`, or `major`
```

> [!TIP]
>
> Run `uv version --help` to see uv's options for automatic SemVer version bumping.

### Publishing to Test PyPI

> [!NOTE]
>
> This step is optional, but recommended. You'll need an API token for [Test PyPI](https://test.pypi.org/).

After incrementing the project version, publish the package with:

```shell
make publish-test

# or
uv publish --index testpypi
```

Then paste your Test PyPI token into the prompt when prompted.

Once the package is published, you can then pull it from Test PyPI to test the installation:

```shell
pip install --extra-index-url https://test.pypi.org/simple/ dbt-datadict==<version>
```

> [!TIP]
>
> If you want to validate that the package is installed as intended, consider creating another virtual environment and installing the package there, rather than installing it in the same environment that you're developing in.

> [!WARNING]
>
> For security, PyPI does not allow for a filename to be reused, even once a project has been deleted and recreated:
>
> - [test.pypi.org/help#file-name-reuse](https://test.pypi.org/help/#file-name-reuse)
>
> If you need to republish a release, you'll need to increment the version.

## Publishing to PyPI

Once you're happy with the changes, commit them to a feature branch and open a pull request so the changes can be reviewed.

When the changes are approved and merged into the `main` branch, create a new GitHub Release with a new tag `v<version>`. The release notes should include a summary of the changes made in the release.

Creating the release will trigger a [GitHub Action](../.github/workflows/publish.yml) that will publish the package to PyPI. Validate that the package has been published by checking the GitHub Action and the [PyPI project page](https://pypi.org/p/dbt-datadict).
