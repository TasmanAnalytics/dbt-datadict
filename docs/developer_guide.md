# Developing Locally

1. Install package dependencies, as well as the `dbt-datadict` package itself:

    ```bash
    $ uv sync --all-groups
    ```

2. To build the package locally, run the following command:

    ```bash
    $ uv build
    ```

3. To publish the package to Test PyPI, run the following command:

    ```bash
    $ export TEST_PYPI_TOKEN=<token>  # Replace <token> with your Test PyPI token
    $ uv publish --index testpypi --token $TEST_PYPI_TOKEN
    ```

4. To bump the version of the package, run the following command:

    ```bash
    $ uv version <version>  # Replace <version> with the new version number
    ```

    > **Hint**
    > Run `uv version --help` to see uv's options for automatic SemVer version bumping.

5. To pull the package from Test PyPI, run the following command:

    ```bash
    $ python -m pip install --extra-index-url https://test.pypi.org/simple/ dbt-datadict==<version>
    ```

    > **Hint**
    > If you want to validate that the package is installed as intended, consider creating another virtual environment and installing the package there, rather than installing it in the same environment that you're developing in.
