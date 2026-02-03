import logging
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

    import subprocess  # noqa: PLC0415

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

    import subprocess  # noqa: PLC0415

    def mock_run(args, **kwargs):  # noqa: unused variables
        return MockCompletedProcess("debug failed!")

    monkeypatch.setattr(subprocess, "run", mock_run)

    error_msg = "Issues encountered when running `dbt debug`. Validate `dbt debug` passes before retrying."
    with caplog.at_level(logging.ERROR):
        result = dbt_io.validate_dbt()

    assert result == False
    assert error_msg in caplog.text


def test__validate_dbt__dbt_deps_fails__false_returned(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """
    If the ``dbt deps`` command is unsuccessful, the validation returns
    ``False`` and logs an error.
    """

    import subprocess  # noqa: PLC0415

    def mock_run(args, **kwargs):  # noqa: unused variables
        if args == ["dbt", "debug"]:
            return MockCompletedProcess("All checks passed!")
        return MockCompletedProcess("deps failed!")

    monkeypatch.setattr(subprocess, "run", mock_run)

    error_msg = "dbt-labs/codegen is required to perform this operation"
    with caplog.at_level(logging.ERROR):
        result = dbt_io.validate_dbt()

    assert result == False
    assert error_msg in caplog.text


@pytest.mark.skip(
    "This is what I'd expect the logging to do, but it actually raises _another_ error (see test below)"
)
def test__validate_dbt__exception_raised__false_returned(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """
    If any part of the validation raises an exception, the validation
    returns ``False`` and logs and error.
    """

    import subprocess  # noqa: PLC0415

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

    import subprocess  # noqa: PLC0415

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

    import subprocess  # noqa: PLC0415

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
    Model YAML can be generated.
    """

    import subprocess  # noqa: PLC0415

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

    import subprocess  # noqa: PLC0415

    def mock_run(args, **kwargs):  # noqa: unused variables
        raise Exception("something went wrong")

    monkeypatch.setattr(subprocess, "run", mock_run)

    error_msg = "Issues encountered when generating the model yaml: something went wrong"
    with caplog.at_level(logging.ERROR):
        result = dbt_io.get_model_yaml(model_names=["foo"])

    assert result is None
    assert error_msg in caplog.text
