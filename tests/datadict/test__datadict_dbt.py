import textwrap

import pytest

from datadict import datadict_dbt


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
    ]
)
def test__bash_output_can_be_parsed(in_: str, expected: str):
    """
    Bash output can be parsed to extract the YAML content.
    """

    result = datadict_dbt.parse_bash_outputs(in_)

    assert result == expected
