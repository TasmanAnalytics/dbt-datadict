# Developer guide

## Configuring a local environment

This is a Python project which uses [uv](https://github.com/astral-sh/uv) for package management.

### Prerequisites: Installing Nix (Recommended)

This project includes a Nix flake that provides a reproducible development environment with all required tools. We recommend using the [Determinate Systems Nix installer](https://determinate.systems/posts/determinate-nix-installer):

```shell
# macOS, Linux, or WSL (Windows Subsystem for Linux)
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
```

> [!NOTE]
>
> **Windows users:** We recommend using WSL (Windows Subsystem for Linux) to run Nix. Follow the [WSL installation guide](https://learn.microsoft.com/en-us/windows/wsl/install) first, then install Nix inside your WSL environment.

After installation, you may need to restart your terminal or reboot your system for the `nix` command to become available.

### Quick Start: Using the Nix Flake (Recommended)

Once Nix is installed, enter the development environment with:

```shell
nix develop -c $SHELL
```

This will:
- Automatically install all required dependencies (Python, uv, git, etc.)
- Set up the Python virtual environment using uv
- Install pre-commit hooks
- Launch your preferred shell (zsh, bash, fish, etc.)

The [Makefile](https://github.com/TasmanAnalytics/dbt-datadict/blob/main/Makefile) has several commands to help with development tasks:

```shell
make build  # Build the package locally
make test   # Run the tests
make lint   # Run the linters
make docs   # Build and serve the documentation locally
```

> [!TIP]
>
> Create a shell alias for convenience:
> ```shell
> alias nixdev='nix develop -c $SHELL'
> ```

### Alternative Setup: Manual Installation

If you prefer not to use Nix, you can set up the environment manually.

The [Makefile](https://github.com/TasmanAnalytics/dbt-datadict/blob/main/Makefile) includes a command to install uv and sync dependencies:

```shell
make uv     # Install uv, sync dependencies, install pre-commit hooks
```

If you're using a system without `make`, you can run the equivalent commands directly:

```shell
# Install uv and sync dependencies (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --all-groups
uv run pre-commit install --install-hooks

# Install uv and sync dependencies (Windows)
# First, review the installation script:
powershell -c "irm https://astral.sh/uv/install.ps1 | more"
# Then, if you're happy with it, install:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

uv sync --all-groups
uv run pre-commit install --install-hooks

# Build the package locally
uv build

# Run the tests
uv run pytest -v

# Run the linters
uv run pre-commit run --all-files --hook-stage pre-commit
uv run pre-commit run --all-files --hook-stage pre-push

# Build and serve the documentation locally
uv run mkdocs build
uv run mkdocs serve
```

## Publishing a new release

To publish a new release of the package to PyPI, you'll need to increment the project version and create a new release on GitHub.

### Incrementing the version

Update the version in the [`pyproject.toml`](https://github.com/TasmanAnalytics/dbt-datadict/blob/main/pyproject.toml) file, where the version specified is in line with the [PyPA Version Specifiers specification](https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers). You can either manually update the version or use `uv` commands:

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

Creating the release will trigger a [GitHub Action](https://github.com/TasmanAnalytics/dbt-datadict/blob/main/.github/workflows/publish.yml) that will publish the package to PyPI. Validate that the package has been published by checking the GitHub Action and the [PyPI project page](https://pypi.org/p/dbt-datadict).
