# Developing Locally

1. Install package dependencies

    ```bash
    $ poetry install
    ```

2. To build the package locally, run the following command:

    ```bash
    $ poetry build
    ```

3. To configure `poetry` to publish the package to Test PyPI, run the following:

    ```bash
    $ export TEST_PYPI_TOKEN=<token>  # Replace <token> with your Test PyPI token
    $ poetry config pypi-token.testpypi $TEST_PYPI_TOKEN
    $ poetry config repositories.testpypi https://test.pypi.org/legacy/
    ```

4. To publish the package to Test PyPI, run the following command:

    ```bash
    $ poetry publish --repository testpypi
    ```

5. To bump the version of the package, run the following command:

    ```bash
    $ poetry version <version>  # Replace <version> with the new version number
    ```

    > **Hint**
    > Run `poetry version --help` to see Poetry's options for automatic SemVer version bumping.

6. To pull the package from Test PyPI, run the following command:

    ```bash
    $ python -m pip install --extra-index-url https://test.pypi.org/simple/ dbt-datadict==<version>  # Replace <version>
    ```

    > **Hint**
    > If you want to validate that the package is installed as intended, consider creating another virtual environment and installing the package there, rather than installing it in the same environment that you're developing in.