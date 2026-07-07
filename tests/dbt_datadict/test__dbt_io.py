import logging
import subprocess
import textwrap
import types
from typing import Any

import pytest

from dbt_datadict import dbt_io


@pytest.mark.parametrize(
    "in_, expected",
    [
        # typical case
        (
            textwrap.dedent(
                """\
                12:34:56  Running with dbt=1.2.3
                12:34:57  Registered adapter: foobar=7.8.9
                12:34:58  Found 4 models, 1 operation, 8 data tests, 123 macros
                version: 2
                models:
                  - name: foo
                    description: This is a test model.
                    columns:
                      - name: bar
                        data_type: string
                        description: This is a test column.
                """
            ),
            (
                textwrap.dedent(
                    """\
                    version: 2
                    models:
                      - name: foo
                        description: This is a test model.
                        columns:
                          - name: bar
                            data_type: string
                            description: This is a test column.
                    """
                )
            ),
        ),
        # other cases
        ("", ""),
        ("foo bar", ""),
        ("version: 1", ""),
        (
            textwrap.dedent(
                """\
                12:34:56  Running with dbt=1.2.3
                12:34:57  Registered adapter: foobar=7.8.9
                12:34:58  Found 4 models, 1 operation, 8 data tests, 123 macros
                22:02:07  Encountered an error while running operation: Compilation Error
                  Macro 'macro.codegen.generate_model_yaml' (macros/generate_model_yaml.sql) depends on a node named 'foo' which was not found

                  > in macro default__generate_model_yaml (macros/generate_model_yaml.sql)
                  > called by macro generate_model_yaml (macros/generate_model_yaml.sql)
                  > called by <Unknown>
                """
            ),
            "",
        ),
    ],
)
def test__bash_output_can_be_parsed(in_: str, expected: str):
    """
    Bash output can be parsed to extract the YAML content.
    """

    result = dbt_io.parse_bash_outputs(in_)

    assert result == expected


@pytest.mark.skip(
    "This is what I'd expect the logging to do, but it actually raises _another_ error (see test below)"
)
def test__parse_bash_outputs__exception_raised__error_logged(
    caplog: pytest.LogCaptureFixture,
):
    """
    When parsing bash output raises an exception, the exception is logged as
    an error.

    Future refactoring should result in this test being binned.
    """

    error_msg = "There was an issue parsing the codegen outputs:"
    with caplog.at_level(logging.ERROR):
        result = dbt_io.parse_bash_outputs(None)  # type: ignore

    assert result is None
    assert error_msg in caplog.text


def test__parse_bash_outputs__exception_raised__different_exception_raised(
    capsys: pytest.CaptureFixture,
):
    """
    This is just to "document" the existing behaviour, which I assume is not
    intentional.

    Future refactoring should result in this test being binned.
    """

    with pytest.raises(
        TypeError,
        match=r'can only concatenate str \(not "AttributeError"\) to str',
    ):
        dbt_io.parse_bash_outputs(None)  # type: ignore


class MockCompletedProcess:
    def __init__(self, returns: Any):
        self.stdout = types.SimpleNamespace(decode=lambda _: returns)


def test__validate_dbt__happy_path__true_returned(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """
    If the `dbt debug` command is unsuccessful, the validation returns
    ``False`` and logs an error.
    """

    def mock_run(args, **kwargs):  # noqa: unused variables
        if args == ["dbt", "debug"]:
            return MockCompletedProcess("All checks passed!")
        return MockCompletedProcess("dbt-labs/codegen")

    monkeypatch.setattr(subprocess, "run", mock_run)

    info_msg = "dbt project successfully validated"
    with caplog.at_level(logging.INFO):
        result = dbt_io.validate_dbt()

    assert result == True
    assert info_msg in caplog.text


def test__validate_dbt__dbt_debug_fails__false_returned(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """
    If the ``dbt debug`` command is unsuccessful, the validation returns
    ``False`` and logs an error.
    """

    def mock_run(args, **kwargs):  # noqa: unused variables
        return MockCompletedProcess("debug failed!")

    monkeypatch.setattr(subprocess, "run", mock_run)

    error_msg = "Issues encountered when running `dbt debug`. Validate `dbt debug` passes before retrying."
    with caplog.at_level(logging.ERROR):
        result = dbt_io.validate_dbt()

    assert result == False
    assert error_msg in caplog.text


def test__validate_dbt__codegen_missing__warning_logged_true_returned(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """
    If ``dbt-labs/codegen`` is not found, validation returns True with a warning
    (codegen is now optional; manifest-based extraction is used if available).
    """

    def mock_run(args, **kwargs):  # noqa: unused variables
        if args == ["dbt", "debug"]:
            return MockCompletedProcess("All checks passed!")
        return MockCompletedProcess("deps completed!")

    monkeypatch.setattr(subprocess, "run", mock_run)

    warning_msg = "dbt-labs/codegen not found - will use manifest for column metadata if available"
    with caplog.at_level(logging.WARNING):
        result = dbt_io.validate_dbt()

    assert result == True
    assert warning_msg in caplog.text


@pytest.mark.skip(
    "This is what I'd expect the logging to do, but it actually raises _another_ error (see test below)"
)
def test__validate_dbt__exception_raised__false_returned(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """
    If any part of the validation raises an exception, the validation
    returns ``False`` and logs an error.
    """

    def mock_run(args, **kwargs):  # noqa: unused variables
        raise Exception("something broke")

    monkeypatch.setattr(subprocess, "run", mock_run)

    error_msg = (
        "Issues encountered when attempting to validate dbt: something broke"
    )
    with caplog.at_level(logging.ERROR):
        result = dbt_io.validate_dbt()

    assert result == False
    assert error_msg in caplog.text


def test__validate_dbt__exception_raised__different_exception_raised(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """
    This is just to "document" the existing behaviour, which I assume is not
    intentional.

    Future refactoring should result in this test being binned.
    """

    def mock_run(args, **kwargs):  # noqa: unused variables
        raise Exception

    monkeypatch.setattr(subprocess, "run", mock_run)

    with pytest.raises(
        TypeError,
        match=r'can only concatenate str \(not "Exception"\) to str',
    ):
        dbt_io.validate_dbt()


def test__get_model_yaml__happy_path__model_yaml_returned_as_dict(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """
    Model YAML can be generated.
    """

    mock_generated_model_yaml = textwrap.dedent(
        """\
        12:34:56  Running with dbt=1.2.3
        12:34:57  Registered adapter: foobar=7.8.9
        12:34:58  Found 4 models, 1 operation, 8 data tests, 123 macros
        version: 2
        models:
          - name: foo
            description: This is a test model.
            columns:
              - name: bar
                data_type: string
                description: This is a test column.
        """
    )

    def mock_run(args, **kwargs):  # noqa: unused variables
        return MockCompletedProcess(mock_generated_model_yaml)

    monkeypatch.setattr(subprocess, "run", mock_run)

    model_yaml = dbt_io.get_model_yaml(model_names=["foo"])
    expected_yaml = {
        "version": 2,
        "models": [
            {
                "name": "foo",
                "description": "This is a test model.",
                "columns": [
                    {
                        "name": "bar",
                        "data_type": "string",
                        "description": "This is a test column.",
                    },
                ],
            },
        ],
    }

    assert model_yaml == expected_yaml


def test__get_model_yaml__compilation_error__no_data_returned(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """
    If the YAML generation encounters a compilation error, no YAML dict is
    returned and the error is logged.
    """

    def mock_run(args, **kwargs):  # noqa: unused variables
        return MockCompletedProcess("Compilation Error")

    monkeypatch.setattr(subprocess, "run", mock_run)

    error_msg = (
        "Issues encountered when generating the model yaml: Compilation Error"
    )
    with caplog.at_level(logging.ERROR):
        model_yaml = dbt_io.get_model_yaml(model_names=["foo"])

    assert model_yaml is None
    assert error_msg in caplog.text


def test__get_model_yaml__exception_raised__no_data_returned(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """
    If any part of the YAML generation raises an exception, the exception is
    logged.
    """

    def mock_run(args, **kwargs):  # noqa: unused variables
        raise Exception("something went wrong")

    monkeypatch.setattr(subprocess, "run", mock_run)

    error_msg = "Issues encountered when generating the model yaml: something went wrong"
    with caplog.at_level(logging.ERROR):
        result = dbt_io.get_model_yaml(model_names=["foo"])

    assert result is None
    assert error_msg in caplog.text


# Tests for manifest-based extraction


def test__get_manifest_path__found__returns_absolute_path(
    tmp_path: Any,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    When manifest exists in target/ directory, get_manifest_path returns absolute path.
    """
    monkeypatch.chdir(tmp_path)

    dbt_project_file = tmp_path / "dbt_project.yml"
    dbt_project_file.write_text("name: test_project")

    manifest_dir = tmp_path / "target"
    manifest_dir.mkdir()
    manifest_file = manifest_dir / "manifest.json"
    manifest_file.write_text("{}")

    result = dbt_io.get_manifest_path()

    assert result is not None
    assert result.endswith("manifest.json")


def test__get_manifest_path__not_in_dbt_project__returns_none(
    tmp_path: Any,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """
    When not in a dbt project directory, get_manifest_path returns None and logs error.
    """
    monkeypatch.chdir(tmp_path)

    with caplog.at_level(logging.ERROR):
        result = dbt_io.get_manifest_path()

    assert result is None
    assert "Not in a dbt project directory" in caplog.text


def test__is_manifest_fresh__fresh__returns_true(
    tmp_path: Any,
):
    """
    When manifest was generated recently, is_manifest_fresh returns True.
    """
    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(
        '{"metadata": {"generated_at": "2099-07-07T08:52:26.321188Z"}}'
    )

    result = dbt_io.is_manifest_fresh(str(manifest_file))

    assert result is True


def test__is_manifest_fresh__stale__returns_false(
    tmp_path: Any,
    caplog: pytest.LogCaptureFixture,
):
    """
    When manifest is older than max_age_hours, is_manifest_fresh returns False.
    """
    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(
        '{"metadata": {"generated_at": "2020-07-07T08:52:26.321188Z"}}'
    )

    with caplog.at_level(logging.WARNING):
        result = dbt_io.is_manifest_fresh(str(manifest_file))

    assert result is False
    assert "hours old" in caplog.text


def test__generate_manifest__success__returns_true(
    tmp_path: Any,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """
    When dbt parse succeeds, generate_manifest returns True.
    """

    def mock_run(args, **kwargs):  # noqa: unused variables
        if args[0:2] == ["dbt", "parse"]:
            manifest_file = tmp_path / "target" / "manifest.json"
            manifest_file.parent.mkdir(parents=True, exist_ok=True)
            manifest_file.write_text("{}")
            return types.SimpleNamespace(returncode=0, stderr=b"")
        return types.SimpleNamespace(returncode=0, stderr=b"")

    monkeypatch.setattr(subprocess, "run", mock_run)
    monkeypatch.chdir(tmp_path)

    info_msg = "Manifest generated successfully"
    with caplog.at_level(logging.INFO):
        result = dbt_io.generate_manifest()

    assert result is True
    assert info_msg in caplog.text


def test__generate_manifest__failure__returns_false(
    tmp_path: Any,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """
    When dbt parse fails, generate_manifest returns False and logs error.
    """

    def mock_run(args, **kwargs):  # noqa: unused variables
        return types.SimpleNamespace(
            returncode=1, stderr=b"dbt parse failed"
        )

    monkeypatch.setattr(subprocess, "run", mock_run)

    error_msg = "dbt parse failed"
    with caplog.at_level(logging.ERROR):
        result = dbt_io.generate_manifest()

    assert result is False
    assert error_msg in caplog.text


def test__extract_columns_from_manifest_streaming__success__returns_models(
    tmp_path: Any,
):
    """
    extract_columns_from_manifest_streaming successfully extracts model columns.
    """
    manifest_content = """{
    "metadata": {
        "generated_at": "2099-07-07T08:52:26.321188Z"
    },
    "nodes": {
        "model.project.test_model": {
            "name": "test_model",
            "resource_type": "model",
            "columns": {
                "col1": {
                    "name": "col1",
                    "data_type": "varchar",
                    "description": "Column 1"
                },
                "col2": {
                    "name": "col2",
                    "data_type": "integer",
                    "description": "Column 2"
                }
            }
        }
    }
}"""
    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(manifest_content)

    result = dbt_io.extract_columns_from_manifest_streaming(
        str(manifest_file), ["test_model"]
    )

    assert result is not None
    assert result["version"] == 2
    assert len(result["models"]) == 1
    assert result["models"][0]["name"] == "test_model"
    assert len(result["models"][0]["columns"]) == 2

    col_names = [c["name"] for c in result["models"][0]["columns"]]
    assert col_names == ["col1", "col2"]


def test__extract_columns_from_manifest_streaming__model_not_found__returns_none(
    tmp_path: Any,
    caplog: pytest.LogCaptureFixture,
):
    """
    When model not in manifest, returns None and logs warning.
    """
    manifest_content = '{"metadata": {}, "nodes": {}}'
    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(manifest_content)

    with caplog.at_level(logging.WARNING):
        result = dbt_io.extract_columns_from_manifest_streaming(
            str(manifest_file), ["missing_model"]
        )

    assert result is None
    assert "No models found in manifest" in caplog.text


def test__get_model_yaml__from_manifest__success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Any,
):
    """
    get_model_yaml successfully extracts from manifest when available.
    """
    monkeypatch.chdir(tmp_path)

    dbt_project_file = tmp_path / "dbt_project.yml"
    dbt_project_file.write_text("name: test_project")

    manifest_content = """{
    "metadata": {
        "generated_at": "2099-07-07T08:52:26.321188Z"
    },
    "nodes": {
        "model.project.test_model": {
            "name": "test_model",
            "resource_type": "model",
            "columns": {
                "col1": {
                    "name": "col1",
                    "data_type": "varchar",
                    "description": "Test column"
                }
            }
        }
    }
}"""
    manifest_dir = tmp_path / "target"
    manifest_dir.mkdir()
    manifest_file = manifest_dir / "manifest.json"
    manifest_file.write_text(manifest_content)

    result = dbt_io.get_model_yaml(["test_model"])

    assert result is not None
    assert result["version"] == 2
    assert len(result["models"]) == 1
    assert result["models"][0]["name"] == "test_model"


def test__get_model_yaml__fallback_to_database__when_manifest_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Any,
    caplog: pytest.LogCaptureFixture,
):
    """
    When manifest is missing, get_model_yaml falls back to database approach.
    """
    monkeypatch.chdir(tmp_path)

    dbt_project_file = tmp_path / "dbt_project.yml"
    dbt_project_file.write_text("name: test_project")

    mock_generated_model_yaml = textwrap.dedent(
        """\
        version: 2
        models:
          - name: test_model
            description: Test model
            columns:
              - name: col1
                data_type: varchar
                description: Test column
        """
    )

    def mock_run(args, **kwargs):  # noqa: unused variables
        return MockCompletedProcess(mock_generated_model_yaml)

    monkeypatch.setattr(subprocess, "run", mock_run)

    fallback_msg = "Falling back to database query"
    with caplog.at_level(logging.INFO):
        result = dbt_io.get_model_yaml(["test_model"])

    assert result is not None
    assert result["models"][0]["name"] == "test_model"
    assert fallback_msg in caplog.text
