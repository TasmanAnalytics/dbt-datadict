[![tasman_logo][tasman_wordmark_black]][tasman_website_light_mode]
[![tasman_logo][tasman_wordmark_cream]][tasman_website_dark_mode]

---

*We are the boutique analytics consultancy that turns disorganised data into real business value. [Get in touch](https://tasman.ai/contact/) to learn more about how Tasman can help solve your organisations data challenges.*

# dbt-datadict

dbt-datadict is a CLI tool that provides helpful functions to improve the speed and efficiency of managing column-level documentation across large dbt projects.

**Key Features:**

1. Rapid creation of model yaml files, leveraging dbt-labs/codegen 💥 (no more copy/pasting from the terminal 🙌)
2. In-place updates to model yaml on schema changes 🧙
3. Consolidatation of column descriptions into a data dictionary 📓
4. Keeps column descriptions in sync with a single command 🔃

## Installation ⏬

Install dbt-datadict using
    
    ```bash
    $ python -m pip install dbt-datadict
    ```

## Getting Started 🚀

[Full user guide](docs/user_guide.md) 🧑‍🏫

### Command: `generate`

This command generates yaml files using the dbt-codegen package. Where it finds existing model yaml files, it will merge the full column lists. For missing models, it will create a separate model yaml file using the name provided.

> **Warning ⚠️**  
> This command will only run in a valid dbt project with the dbt-labs/codegen dbt package installed.

#### **Usage:**
```bash
$ datadict generate [-D <DIRECTORY>] [-f <NAME>] 
```

#### **Options:**

- **`-D, --directory <DIRECTORY>`**: Directory to search for models. Default: 'models/'.
- **`-f, --file <NAME>`**: The yaml file to store new model configurations that aren't referenced in an existing yaml file.
- **`--sort`**: Triggers the generated YAML files to be sorted alphabetically (on by default). 
- **`--unique-model-yaml`**: Creates one YAML for each model with the same name as the model.

### Command: **`apply`**

This command applies data dictionary updates to all model YAML files in the specified directory and its subdirectories.

#### **Usage:**
```bash
$ datadict apply [-D <DIRECTORY>] [-d <DICTIONARY>] 
```

#### **Options:**

- **`-D, --directory <DIRECTORY>`**: Directory to search for fields and apply the dictionary to. Default: 'models/'.
- **`-d, --dictionary <DICTIONARY>`**: Location of the dictionary file. Default: 'datadictionary.yml'.

## ⚠️ Important Note ⚠️

It is highly recommend to only use this library in a version controlled environment, such as git. Additionally, please ensure that you have backed up your model YAML files and data dictionary before applying any updates. The application modifies files in place and does not create backups automatically.

Use this application responsibly and verify the updates before proceeding.

## Contributing
We encourage you to contribute to dbt Data Dictionary! Please check out our [Contributing to dbt Data Dictionary](CONTRIBUTING.md) guide for guidelines about how to proceed.

## License

dbt Data Dictionary is released under the GNU General Public License v3.0. See [LICENSE](LICENSE) for details.

[tasman_website_dark_mode]: https://tasman.ai#gh-dark-mode-only
[tasman_website_light_mode]: https://tasman.ai#gh-light-mode-only
[tasman_wordmark_cream]: https://raw.githubusercontent.com/TasmanAnalytics/.github/master/images/tasman_wordmark_cream_500.png#gh-dark-mode-only
[tasman_wordmark_black]: https://raw.githubusercontent.com/TasmanAnalytics/.github/master/images/tasman_wordmark_black_500.png#gh-light-mode-only