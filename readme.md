# dbt Data Dictionary

The dbt Data Dictionary is a command-line tool that provides helpful tools to improve the process of managing column-level documentation across a large dbt project. It has the following key features:

1. It will analyse your existing dbt project for model yaml files, and for each column summarise the different column description versions, and models that the column appears in.
2. It once set in the dictionary, it will automatically apply descriptions for all columns with the same name (or alias) across the project.

## **How to Use the Application**

### **Installation**

1. Install dbt data dictionary using
    
    ```bash
    pip install dbt-datadict
    ```
    

### **Command-Line Interface (CLI) Usage**

The Data Dictionary Application provides a command-line interface (CLI) that allows you to interact with the library easily.
### Command: `generate`

This command generates yaml files using the dbt-codegen package. Where it finds existing model yaml files, it will merge the full column lists. For missing models, it will create a separate model yaml file using the name provided.

**IMPORTANT**: This command will only run in a valid dbt project with dbt-labs/codegen installed.

### **Usage:**

```bash
$ datadict generate [-d <DICTIONARY>] [-D <DIRECTORY>]
```

### **Options:**

- `-D, --directory <DIRECTORY>`: Directory to apply the dictionary. Default: 'models/'.
- `-f, --file <NAME>`: The file to store any new models in.
- `--sort`: Triggers the generated YAML files to be sorted alphabetically.

### **Generation Process**
1. dbt installation is validated by running `dbt debug` and `dbt deps`
2. The supplied directory is searched recursively for YAML model files.
3. The supplied directory is serach for model files (ending with .sql)
4. dbt-labs/codegen is used to obtain the full column lists for each of the models.
5. Models in existing YAML model files are synchronised with the expected column list.
6. Models that aren't in any existing YAML files are added to the file path supplied in `--file`

### Command: **`apply`**

This command applies data dictionary updates to all model YAML files in the specified directory and its subdirectories.

### **Usage:**

```bash
$ datadict apply [-d <DICTIONARY>] [-D <DIRECTORY>]
```

### **Options:**

- **`-d, --dictionary <DICTIONARY>`**: Location of the dictionary file. Default: 'datadictionary.yml'.
- **`-D, --directory <DIRECTORY>`**: Directory to apply the dictionary. Default: 'models/'.


## Examples

Given the following model yaml file example:

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

Running `dbt_datadict apply` would create a data dictionary as follows:

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

## Developing Locally and distributing

Create the venv

`make init`

Activate the venv

`. .venv/bin/activate`

Building locally

`python setup.py develop`

Building for distribution

`python setup.py sdist bdist_wheel`

Pushing the distribution to Test PyPi (changes require upversioning and access)

`twine upload --repository testpypi --skip-existing dist/*`

Pushing the distribution to Production PyPi (changes require upversioning and access)

`twine upload --repository pypi --skip-existing dist/*`

Pulling a test distribution

`pip install --extra-index-url https://test.pypi.org/simple/ dbt-datadictionary==<version>`

## **Important Note**

It is highly recommend to only use this library in a version controlled environment, such as git. Additionally, please ensure that you have backed up your model YAML files and data dictionary before applying any updates. The application modifies files in place and does not create backups automatically.

Use this application responsibly and verify the updates before proceeding.