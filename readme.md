# dbt datadict

dbt-datadict is a command-line tool that provides helpful tools to improve the process of managing column-level documentation across a large dbt project. It has the following key features:

1. It works alongside dbt-labs/codegen to automate the model documentation creation process. By reviewing the models it can find, it uses codegen to identify the full column list and will merge this with what is already existing ikn the project, adding any missing models to a given file path.
2. It will analyse your existing dbt project for model yaml files, and for each column summarise the different column description versions, and models that the column appears in. Once set in the dictionary, it will automatically apply descriptions for all columns with the same name (or alias) across the project.

## How to use dbt Data Dictionary

### **Installation**

1. Install dbt data dictionary using
    
    ```bash
    $ python -m pip install dbt-datadict
    ```
2. Start using the `datadict` CLI command.
    ```bash
    $ datadict --help
    ```

### Command-Line Interface (CLI) Usage

The Data Dictionary Application provides a command-line interface (CLI) that allows you to interact with the library easily.

#### Command: `generate`

This command generates yaml files using the dbt-codegen package. Where it finds existing model yaml files, it will merge the full column lists. For missing models, it will create a separate model yaml file using the name provided.

> **Warning**
> This command will only run in a valid dbt project with the dbt-labs/codegen dbt package installed.

##### **Usage:**

```bash
$ datadict generate [-D <DIRECTORY>] [-f <NAME>] 
```

##### **Options:**

- **`-D, --directory <DIRECTORY>`**: Directory to apply the dictionary. Default: 'models/'.
- **`-f, --file <NAME>`**: The file to store any new models in.
- **`--sort`**: Triggers the generated YAML files to be sorted alphabetically (on by default).

##### **Generation Process**
1. dbt installation is validated by running `dbt debug` and `dbt deps`
2. The supplied directory is searched recursively for YAML model files (ending with .yml or .yaml).
3. The supplied directory is searched for model files (ending with .sql)
4. dbt-labs/codegen is used to obtain the full column lists for each of the models that we found in the directory.
5. Models in existing YAML model files are synchronised with the expected column list.
6. Models that aren't in any existing YAML files are added to the file path supplied in `--file`

#### Command: **`apply`**

This command applies data dictionary updates to all model YAML files in the specified directory and its subdirectories.

##### **Usage:**

```bash
$ datadict apply [-d <DICTIONARY>] [-D <DIRECTORY>]
```

##### **Options:**

- **`-d, --dictionary <DICTIONARY>`**: Location of the dictionary file. Default: 'datadictionary.yml'.
- **`-D, --directory <DIRECTORY>`**: Directory to apply the dictionary. Default: 'models/'.


## Examples

Given the following dbt model yaml file example:

```yaml
version: 2

models:
  - name: model_1
    columns:
      - name: field_1
        description: 'field_1_description_1'

      - name: field_2
        description: ''

  - name: model_2
    columns:
      - name: field_1
        description: 'field_1_description_2'

      - name: field_3
        description: 'field_3_description_1'
```

Running `datadict apply` would create a data dictionary as follows:

```yaml
dictionary:

  - name: field_1
    description: ''
    description_versions:
      - 'field_1_description_1'
      - 'field_1_description_2'
    models:
      - model_1
      - model_2

  - name: field_2
    description: ''
    models:
      - model_1

  - name: field_3
    description: 'field_3_description_1'
    models:
      - model_2
```

For `field_1` there were two different descriptions detected within the model file, so these are contained within the `description_versions` field in the dictionary. To enable the dictionary to apply a consistent description for `field_1` the user must enter description in the `description` field, and rerun `dbt_datadict apply` .

```yaml
dictionary:

  - name: field_1
    description: 'field_1_new_description'
    description_versions:
      - 'field_1_description_1'
      - 'field_1_description_2'
    models:
      - model_1
      - model_2

  - name: field_2
    description: ''
    models:
      - model_1

  - name: field_3
    description: 'field_3_description_1'
    models:
      - model_2
```

Resulting in an updated model YAML file:

```yaml
version: 2

models:
  - name: model_1
    columns:
      - name: field_1
        description: 'field_1_new_description'

      - name: field_2
        description: ''

  - name: model_2
    columns:
      - name: field_1
        description: 'field_1_new_description'

      - name: field_3
        description: 'field_3_description_1'
```

## Getting Started

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

## **Important Note**

It is highly recommend to only use this library in a version controlled environment, such as git. Additionally, please ensure that you have backed up your model YAML files and data dictionary before applying any updates. The application modifies files in place and does not create backups automatically.

Use this application responsibly and verify the updates before proceeding.

## Contributing
We encourage you to contribute to dbt Data Dictionary! Please check out our [Contributing to dbt Data Dictionary](CONTRIBUTING.md) guide for guidelines about how to proceed.

## License

dbt Data Dictionary is released under the GNU General Public License v3.0. See [LICENSE](LICENSE) for details.
