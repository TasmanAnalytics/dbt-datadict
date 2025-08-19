[![tasman_logo][tasman_wordmark_black]][tasman_website_light_mode]
[![tasman_logo][tasman_wordmark_cream]][tasman_website_dark_mode]

[tasman_website_dark_mode]: https://tasman.ai#gh-dark-mode-only
[tasman_website_light_mode]: https://tasman.ai#gh-light-mode-only
[tasman_wordmark_cream]: https://raw.githubusercontent.com/TasmanAnalytics/.github/master/images/tasman_wordmark_cream_500.png#gh-dark-mode-only
[tasman_wordmark_black]: https://raw.githubusercontent.com/TasmanAnalytics/.github/master/images/tasman_wordmark_black_500.png#gh-light-mode-only

---

_We are the boutique analytics consultancy that turns disorganised data into real business value. [Get in touch](https://tasman.ai/contact/) to learn more about how Tasman can help solve your organisations data challenges._

<span align="center">

<a href="https://github.com/astral-sh/uv"><img alt="uv" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" /></a>
<a href="https://www.python.org/downloads/"><img alt="Python" src="https://img.shields.io/badge/Python-3.10+-blue.svg" /></a>
<a href="https://pypi.python.org/pypi/dbt-datadict"><img alt="PyPI" src="https://img.shields.io/pypi/v/dbt-datadict.svg" /></a>
<a href="https://github.com/TasmanAnalytics/dbt-datadict/actions/workflows/tests.yaml"><img alt="tests" src="https://github.com/TasmanAnalytics/dbt-datadict/actions/workflows/tests.yaml/badge.svg" /></a>

</span>

# dbt-datadict

Tool for managing consistent column descriptions across a dbt project.

**Key features:**

1. Rapid creation of model YAML files, leveraging [dbt-labs/dbt-codegen](https://github.com/dbt-labs/dbt-codegen) 💥 (no more copy/pasting from the terminal 🙌)
2. In-place updates to model YAML on schema changes 🧙
3. Consolidation of column descriptions into a data dictionary 📓
4. Keeps column descriptions in sync with a single command 🔃

## Installation ⏬

Install from PyPI:

```shell
# with pip
pip install dbt-datadict

# with uv
uv add --dev dbt-datadict
```

## Getting started 🚀

> [!TIP]
>
> Check out the full user guide at:
>
> - [docs/user_guide.md](docs/user_guide.md)

Run the tool with the `datadict` command. There are two supported commands:

- `generate`: Generates model YAML files using the [dbt-codegen](https://github.com/dbt-labs/dbt-codegen) package.
- `apply`: Applies data dictionary updates to existing model YAML files.

```shell
datadict generate
datadict apply
```

## ⚠️ Important note ⚠️

It is highly recommend to only use this library in a version controlled environment, such as git. Additionally, please ensure that you have backed up your model YAML files and data dictionary before applying any updates. The application modifies files in place and does not create backups automatically.

Use this application responsibly and verify the updates before proceeding.

## Contributing

We encourage you to contribute to this project! Please check out our [contribution guide](docs/contributing.md) for details.

## License

This tool is released under the GNU General Public License v3.0. See [LICENSE](https://github.com/TasmanAnalytics/dbt-datadict/blob/main/LICENSE) for details.
