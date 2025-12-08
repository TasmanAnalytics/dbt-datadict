import logging
import pathlib
import shutil
import textwrap
from collections.abc import Generator

import pytest
import ruamel.yaml

from dbt_datadict import (
    dbt_io,
    generate,
    utils,
)

HERE = pathlib.Path(__file__).parent
FIXTURES = HERE / "fixtures"


@pytest.fixture
def generated_model_yaml() -> dict:
    """
    dbt's generated model YAML.
    """

    yaml = ruamel.yaml.YAML(typ="unsafe", pure=True)
    generated_yaml = FIXTURES / "generated_model_yaml.yml"

    return yaml.load(generated_yaml.read_text(encoding="utf-8"))


def test__checking_files_for_models_in_not_list_logs_error(
    caplog: pytest.LogCaptureFixture,
):
    """
    Checking files in a non-existent directory logs an error (but does not
    raise an exception).
    """

    error_msg = (
        "Issues encountered when iterating through files to collect models."
    )
    with caplog.at_level(logging.ERROR):
        model_dct = generate.check_files_for_models(None)  # type: ignore
        assert model_dct is None
        assert error_msg in caplog.text


def test__checking_files_for_models_in_bad_file_logs_error(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Checking files in a valid file with invalid contents logs an error (but
    does not raise an exception).

    IMO this _should_ be impossible if the file validation logic is correct.
    Future refactoring should result in this test being binned.
    """

    file_path = "path/to/bad/file.yml"
    # Assume the file above has content which generates the following:
    monkeypatch.setattr(
        utils,
        "open_model_yml_file",
        lambda _: {"status": "valid", "bad-attr": "bad-value"},
    )

    error_msg = f"There was an issue processing file '{file_path}'. Ensure it is formatted correctly and retry."
    with caplog.at_level(logging.ERROR):
        model_dct = generate.check_files_for_models([file_path])
        assert model_dct == {"file_yamls": [], "model_list": []}
        assert error_msg in caplog.text


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
    result = generate.combine_column_lists(current_yml, expected_yml)

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
    result = generate.combine_column_lists(current_yml, expected_yml)

    expected = {"name": "Column2", "data_type": "str", "description": ""}

    assert result["updated"] is True
    assert expected in result["yaml"]["columns"]


def test__column_lists_can_be_combined_when_there_are_additional_columns():
    """
    Column lists can be combined when there are additional columns.
    """

    current_yml = {
        "name": "Model1",
        "columns": [
            {"name": "Column1", "data_type": "int", "meta": "foo"},
            {"name": "Column2", "data_type": "str"},
        ],
    }
    expected_yml = {
        "name": "Model1",
        "columns": [
            {
                "name": "Column1",
                "data_type": "int",
                "meta": "foo",
                "description": "",
            },
        ],
    }
    result = generate.combine_column_lists(current_yml, expected_yml)

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
    result = generate.combine_column_lists(current_yml, expected_yml)

    expected = {"name": "Column1", "data_type": "int", "description": ""}

    assert result["updated"] is True
    assert expected in result["yaml"]["columns"]


def test__updating_bad_files_logs_error(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Updating malformed files logs an error (but does not raise an exception).

    Future refactoring should result in this test being binned.
    """

    file_path = "path/to/bad/file.yml"
    error_msg = (
        f"There was an issue processing file '{file_path}'."
        " This is likely a badly formatted YAML file."
    )
    existing_yaml = [{"file_path": file_path, "file_yaml": "oopsie"}]
    with caplog.at_level(logging.ERROR):
        generate.updated_existing_files(existing_yaml, [{}], sort=True)
        assert error_msg in caplog.text


def test__new_model_yaml_can_be_added_to_existing_file(
    temp_dir: pathlib.Path,
):
    """
    Adding a valid model YAML to an existing YAML file adds it to the file.
    """

    mock_yaml = textwrap.dedent(
        """\
        version: 2
        models:
          - name: model
            columns:
              - name: col
        """
    )
    expected_yaml = textwrap.dedent(
        """\
        version: 2
        models:
          - name: model
            columns:
              - name: col
          - name: some-model
        """
    )
    yaml_path = temp_dir / "some-model.yaml"
    yaml_path.write_text(mock_yaml)

    generate.add_missing_models(
        path=str(yaml_path),
        models=[{"name": "some-model"}],
        sort=True,
    )

    assert yaml_path.read_text() == expected_yaml


def test__empty_model_list_adds_no_models_to_path(
    caplog: pytest.LogCaptureFixture,
    temp_dir: pathlib.Path,
):
    """
    Adding a valid model YAML to an existing YAML file adds it to the file.
    """

    mock_yaml = textwrap.dedent(
        """\
        version: 2
        models:
          - name: model
            columns:
              - name: col
        """
    )
    yaml_path = temp_dir / "some-model.yaml"
    yaml_path.write_text(mock_yaml)
    info_msg = f"No updates to apply to '{yaml_path}'"

    with caplog.at_level(logging.INFO):
        generate.add_missing_models(
            path=str(yaml_path),
            models=[],
            sort=True,
        )
        assert info_msg in caplog.text


def test__adding_invalid_model_yaml_logs_error(
    caplog: pytest.LogCaptureFixture,
    temp_dir: pathlib.Path,
):
    """
    Adding an invalid model YAML to an existing YAML file logs an error (but
    does not raise an exception).
    """

    yaml_path = temp_dir / "some-model.yaml"
    yaml_path.write_text("foo: bar")
    error_msg = (
        f"File '{yaml_path}' has been found and but isn't a valid model file"
    )
    with caplog.at_level(logging.ERROR):
        generate.add_missing_models(
            path=str(yaml_path),
            models=[],
            sort=True,
        )
        assert error_msg in caplog.text


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

    monkeypatch.setattr(dbt_io, "validate_dbt", lambda: True)
    monkeypatch.setattr(
        dbt_io,
        "get_model_yaml",
        lambda _: generated_model_yaml,
    )

    models = temp_dir
    shutil.copytree(
        src=FIXTURES / "consolidated_model_yaml/models__before",
        dst=models,
        ignore=shutil.ignore_patterns("*.sql"),
        dirs_exist_ok=True,
    )

    generate.generate_model_yamls(
        directory=str(models),
        name="generated.yml",
        unique_model_yaml=False,
    )

    schemas = list(_walk(models))
    assert len(schemas) == 4

    # fmt: off
    after = FIXTURES / "consolidated_model_yaml/models__after"
    assert _read(models / "domain/domain.yml") == _read(after / "domain/domain.yml")
    assert _read(models / "generated.yml") == _read(after / "generated.yml")
    assert _read(models / "invalid.yml") == _read(after / "invalid.yml")
    assert _read(models / "staging/staging.yml") == _read(after / "staging/staging.yml")
    # fmt: on


def test__models_can_be_generated_from_yaml_files__unique_model_yaml(
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    temp_dir: pathlib.Path,
    generated_model_yaml: dict,
):
    """
    Model schemas can be generated into individual YAML files.
    """

    monkeypatch.setattr(dbt_io, "validate_dbt", lambda: True)
    monkeypatch.setattr(
        dbt_io,
        "get_model_yaml",
        lambda _: generated_model_yaml,
    )

    models = temp_dir
    shutil.copytree(
        src=FIXTURES / "unique_model_yaml/models__before",
        dst=models,
        dirs_exist_ok=True,
    )

    generate.generate_model_yamls(
        directory=str(models),
        name="does-not-apply-in-this-context.yml",
        unique_model_yaml=True,
    )

    schemas = [f for f in _walk(models) if f.suffix == ".yml"]
    assert len(schemas) == 4

    after = FIXTURES / "unique_model_yaml/models__after"
    # fmt: off
    assert _read(models / "domain/dmn__model.yml") == _read(after / "domain/dmn__model.yml")
    assert _read(models / "intermediate/int__model.yml") == _read(after / "intermediate/int__model.yml")
    assert _read(models / "staging/stg__model_1.yml") == _read(after / "staging/stg__model_1.yml")
    assert _read(models / "staging/stg__model_2.yml") == _read(after / "staging/stg__model_2.yml")
    # fmt: on


def test__models_can_be_generated_from_yaml_files_logs_error(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Errors while generating YAML files logs an error (but does not raise an
    exception).
    """

    # We just need _anything_ in the `try` block to throw an exception
    def mock_validate_dbt():
        raise Exception

    monkeypatch.setattr(dbt_io, "validate_dbt", mock_validate_dbt)

    error_msg = "There was an error generating the YAML files."
    with caplog.at_level(logging.ERROR):
        generate.generate_model_yamls("", "", True)
        assert error_msg in caplog.text


def test__models_generation_exits_early_if_dbt_validation_fails(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Model YAML generation exits early if dbt validation fails.
    """

    monkeypatch.setattr(dbt_io, "validate_dbt", lambda: False)
    with caplog.at_level(logging.INFO):
        generate.generate_model_yamls("", "", True)
        assert caplog.text == ""  # No logging because we exited early


def test__models_generation_updates_no_models_when_no_models_exist(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    temp_dir: pathlib.Path,
):
    """
    No model YAMLs are generated when no SQL files are found.
    """

    monkeypatch.setattr(dbt_io, "validate_dbt", lambda: True)
    monkeypatch.setattr(dbt_io, "get_model_yaml", lambda _: {"models": []})
    info_msg = "There are no models to be added."
    with caplog.at_level(logging.INFO):
        generate.generate_model_yamls(str(temp_dir), "", False)
        assert info_msg in caplog.text
