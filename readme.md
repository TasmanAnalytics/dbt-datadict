# dbt datadict

dbt-datadict is a command-line tool that provides helpful tools to improve the process of managing column-level documentation across a large dbt project. It has the following key features:

1. It works alongside dbt-labs/codegen to automate the model documentation creation process. By reviewing the models it can find, it uses codegen to identify the full column list and will merge this with what is already existing ikn the project, adding any missing models to a given file path.
2. It will analyse your existing dbt project for model yaml files, and for each column summarise the different column description versions, and models that the column appears in. Once set in the dictionary, it will automatically apply descriptions for all columns with the same name (or alias) across the project.

## **Installation**

1. Install dbt data dictionary using
    
    ```bash
    $ python -m pip install dbt-datadict
    ```
2. Start using the `datadict` CLI command.
    ```bash
    $ datadict --help
    ```

## Getting Started

[Full user guide](docs/user_guide.md)

### Command: `generate`

This command generates yaml files using the dbt-codegen package. Where it finds existing model yaml files, it will merge the full column lists. For missing models, it will create a separate model yaml file using the name provided.

> **Warning**
> This command will only run in a valid dbt project with the dbt-labs/codegen dbt package installed.

#### **Usage:**
```bash
$ datadict generate [-D <DIRECTORY>] [-f <NAME>] 
```

#### **Options:**

- **`-D, --directory <DIRECTORY>`**: Directory to apply the dictionary. Default: 'models/'.
- **`-f, --file <NAME>`**: The file to store any new models in.
- **`--sort`**: Triggers the generated YAML files to be sorted alphabetically (on by default). 

### Command: **`apply`**

This command applies data dictionary updates to all model YAML files in the specified directory and its subdirectories.

#### **Usage:**
```bash
$ datadict apply [-D <DIRECTORY>] [-d <DICTIONARY>] 
```

#### **Options:**

- **`-D, --directory <DIRECTORY>`**: Directory to apply the dictionary. Default: 'models/'.
- **`-d, --dictionary <DICTIONARY>`**: Location of the dictionary file. Default: 'datadictionary.yml'.



## **Important Note**

It is highly recommend to only use this library in a version controlled environment, such as git. Additionally, please ensure that you have backed up your model YAML files and data dictionary before applying any updates. The application modifies files in place and does not create backups automatically.

Use this application responsibly and verify the updates before proceeding.

## Contributing
We encourage you to contribute to dbt Data Dictionary! Please check out our [Contributing to dbt Data Dictionary](CONTRIBUTING.md) guide for guidelines about how to proceed.

## License

dbt Data Dictionary is released under the GNU General Public License v3.0. See [LICENSE](LICENSE) for details.
