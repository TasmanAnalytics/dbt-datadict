# Package Release Process

1. Once you have made all the necessary changes to the package, update the version in the `pyproject.toml` file by running the following command, where the version specified is in line with the [PyPA Version Specifiers specification](https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers).

    ```bash
    poetry version <version>
    ```

    > **Hint**
    > Run `poetry version --help` to see Poetry's options for automatic SemVer version bumping.

2. Commit the changes to the `pyproject.toml` file.
3. Once the `main` branch is in a release-ready state, create a new GitHub Release with a new tag `v<version>`. The release notes should include a summary of the changes made in the release.
4. Creating the release will trigger a [GitHub Action](../.github/workflows/publish.yml) that will publish the package to PyPI. Validate that the package has been published by checking the GH Action and the [PyPI project page](https://pypi.org/p/dbt-datadict).
