import pathlib
import shutil
from typing import Generator

import pytest
import ruamel.yaml

from datadict import datadict_dbt, datadict_yaml

HERE = pathlib.Path(__file__).parent
FIXTURES = HERE / "fixtures"


@pytest.fixture
def generated_model_yaml() -> dict:
    """
    dbt's generated model YAML.
    """

    yaml = ruamel.yaml.YAML(typ="unsafe", pure=True)
    generated_yaml = FIXTURES / f"generated_model_yaml.yml"

    return yaml.load(
        generated_yaml.read_text(encoding="utf-8")
    )


def test__column_lists_can_be_combined_with_no_missing_columns():
    """
    Column lists can be combined when there are no missing columns.
    """

    current_yml = {
        "name": "Model1",
        "columns": [
            {"name": "Column1", "data_type": "int"},
            {"name": "Column2", "data_type": "str"},
        ],
    }
    expected_yml = {
        "columns": [
            {"name": "Column1", "data_type": "int"},
            {"name": "Column2", "data_type": "str"},
        ]
    }
    result = datadict_yaml.combine_column_lists(current_yml, expected_yml)

    assert result["updated"] is False
    assert result["yaml"] == current_yml


def test__column_lists_can_be_combined_when_there_are_missing_columns():
    """
    Column lists can be combined when there are missing columns.
    """

    current_yml = {
        "name": "Model1",
        "columns": [
            {"name": "Column1", "data_type": "int"},
        ],
    }
    expected_yml = {
        "columns": [
            {"name": "Column1", "data_type": "int"},
            {"name": "Column2", "data_type": "str"},
        ]
    }
    result = datadict_yaml.combine_column_lists(current_yml, expected_yml)

    assert result["updated"] is True
    assert {"name": "Column2", "data_type": "str", "description": ""} in result["yaml"]["columns"]


def test__column_lists_can_be_combined_when_there_are_additional_columns():
    """
    Column lists can be combined when there are additional columns.
    """

    current_yml = {
        "name": "Model1",
        "columns": [
            {"name": "Column1", "data_type": "int"},
            {"name": "Column2", "data_type": "str"},
        ],
    }
    expected_yml = {
        "name": "Model1",
        "columns": [
            {"name": "Column1", "data_type": "int", "description": ""},
        ],
    }
    result = datadict_yaml.combine_column_lists(current_yml, expected_yml)

    assert result["updated"] is True
    assert result["yaml"] == expected_yml


def test__column_lists_can_be_combined_with_empty_model():
    """
    Column lists can be combined when the model file has no columns.
    """

    current_yml = {"name": "Model1"}
    expected_yml = {
        "columns": [
            {"name": "Column1", "data_type": "int"},
        ]
    }
    result = datadict_yaml.combine_column_lists(current_yml, expected_yml)

    assert result["updated"] is True
    assert {"name": "Column1", "data_type": "int", "description": ""} in result["yaml"]["columns"]


def _read(file: pathlib.Path) -> str:
    return file.read_text(encoding="utf-8").strip()


def _walk(directory: pathlib.Path) -> Generator[pathlib.Path, None, None]:
    """
    Return a generator that yields all files in the directory and its
    subdirectories.
    """

    for path in directory.iterdir():
        if path.is_file():
            yield path
        else:
            yield from _walk(path)


def test__models_can_be_generated_from_yaml_files__consolidated_model_yaml(
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    temp_dir: pathlib.Path,
    generated_model_yaml: dict,
):
    """
    Model schemas can be generated into consolidated YAML files.
    """

    monkeypatch.setattr(datadict_dbt, "validate_dbt", lambda: True)
    monkeypatch.setattr(datadict_dbt, "get_model_yaml", lambda _: generated_model_yaml)

    directory = temp_dir
    shutil.copytree(
        src=FIXTURES / "consolidated_model_yaml/models__before",
        dst=directory,
        ignore=shutil.ignore_patterns("*.sql"),
        dirs_exist_ok=True,
    )

    datadict_yaml.generate_model_yamls(
        directory=str(directory),
        name="generated.yml",
        unique_model_yaml=False,
    )

    schemas = list(_walk(directory))
    assert len(schemas) == 4

    # Usually you don't want to loop in tests, but I don't know the nicer
    # way to do this 🤷
    for schema in schemas:
        assert (
            _read(schema)
            == _read(FIXTURES / f"consolidated_model_yaml/models__after/{schema.name}")
        )


def test__models_can_be_generated_from_yaml_files__unique_model_yaml(
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    temp_dir: pathlib.Path,
    generated_model_yaml: dict,
):
    """
    Model schemas can be generated into individual YAML files.
    """

    monkeypatch.setattr(datadict_dbt, "validate_dbt", lambda: True)
    monkeypatch.setattr(datadict_dbt, "get_model_yaml", lambda _: generated_model_yaml)

    directory = temp_dir
    shutil.copytree(
        src=FIXTURES / "unique_model_yaml/models__before",
        dst=directory,
        dirs_exist_ok=True,
    )

    datadict_yaml.generate_model_yamls(
        directory=str(directory),
        name="does-not-apply-in-this-context.yml",
        unique_model_yaml=True,
    )

    schemas = [f for f in _walk(directory) if f.suffix == ".yml"]
    assert len(schemas) == 4

    # Usually you don't want to loop in tests, but I don't know the nicer
    # way to do this 🤷
    for schema in schemas:
        assert (
            _read(schema)
            == _read(FIXTURES / f"unique_model_yaml/models__after/{schema.name}")
        )
