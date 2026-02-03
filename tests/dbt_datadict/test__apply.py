import logging
import os
import pathlib
from typing import TypeAlias

import pytest
from ruamel.yaml.compat import StreamType

from dbt_datadict import apply, utils

ValidModel: TypeAlias = tuple[pathlib.Path, dict]


def _yaml_dumps(content: StreamType, path: pathlib.Path) -> None:
    with open(path, "w") as f:
        utils.YAML.dump(content, f)


def _yaml_loads(path: pathlib.Path) -> StreamType:
    with open(path) as f:
        return utils.YAML.load(f)


@pytest.fixture(scope="function")
def dictionary_file(temp_dir: pathlib.Path) -> pathlib.Path:
    """
    A temporary dictionary YAML file.
    """

    file_path = temp_dir / "test_dictionary.yml"
    file_path.write_text("dictionary:\n")

    return file_path


@pytest.fixture(scope="function")
def datadict_instance(dictionary_file: pathlib.Path) -> apply.DataDict:
    """
    A DataDict instance in the temporary directory.
    """

    return apply.DataDict(str(dictionary_file))


@pytest.fixture(scope="function")
def valid_model(temp_dir: pathlib.Path) -> ValidModel:
    """
    A valid model's path and content.
    """

    model_yaml = {
        "models": [
            {
                "name": "test_model",
                "columns": [
                    {
                        "name": "field1",
                        "description": "Some description.",
                    },
                ],
            },
        ],
    }
    model_yaml_file = temp_dir / "model_file.yml"
    with open(model_yaml_file, "w") as file:
        utils.YAML.dump(model_yaml, file)

    return model_yaml_file, model_yaml


def test__dictionary_can_be_loaded(dictionary_file: pathlib.Path):
    """
    A dictionary can be loaded correctly.
    """

    loaded_dict = apply.load_or_create_dictionary(str(dictionary_file))

    assert isinstance(loaded_dict, dict)


def test__dictionary_cannot_be_loaded_if_not_exists(
    temp_dir: pathlib.Path,
):
    """
    A dictionary cannot be loaded if it doesn't exist.
    """

    non_existent_dict_file = temp_dir / "some/nested/path/non_existent_dict.yml"
    with pytest.raises(FileNotFoundError):
        apply.load_or_create_dictionary(str(non_existent_dict_file))


def test__dictionary_can_be_created(
    temp_dir: pathlib.Path,
    datadict_instance: apply.DataDict,
):
    """
    A new dictionary can be created.
    """

    new_dict_file = temp_dir / "new_dict.yml"
    new_dict_file.parent.mkdir(parents=True, exist_ok=True)
    created_dict = apply.load_or_create_dictionary(str(new_dict_file))

    assert isinstance(created_dict, dict)
    assert new_dict_file.exists()


def test__dictionary_can_be_updated(datadict_instance: apply.DataDict):
    """
    A dictionary can be updated with new fields.
    """

    original = {
        "dictionary": [
            {"name": "field_1"},
            {"name": "field_2", "description": "field_2_description"},
            {
                "name": "field_3",
                "description": "field_3_description",
                "aliases": ["field_3_alias1"],
            },
        ]
    }
    formatted_yaml = apply._format_dictionary(original)

    expected = {
        "dictionary": [
            {"name": "field_1", "description": "", "aliases": []},
            {
                "name": "field_2",
                "description": "field_2_description",
                "aliases": [],
            },
            {
                "name": "field_3",
                "description": "field_3_description",
                "aliases": ["field_3_alias1"],
            },
        ]
    }
    assert formatted_yaml == expected


def test__dictionary_can_be_parsed_without_aliases(
    datadict_instance: apply.DataDict,
):
    """
    A dictionary can be parsed correctly without aliases.
    """

    dictionary = {"dictionary": [{"name": "field1"}, {"name": "field2"}]}
    result = apply._parse_aliases(dictionary)

    assert result == ["field1", "field2"]


def test__dictionary_can_be_parsed_with_aliases(
    datadict_instance: apply.DataDict,
):
    """
    A dictionary can be parsed correctly with aliases.
    """

    test_dictionary = {
        "dictionary": [
            {"name": "field1", "aliases": ["f1", "alias1"]},
            {"name": "field2"},
        ]
    }
    result = apply._parse_aliases(test_dictionary)

    assert result == ["field1", "f1", "alias1", "field2"]


def test__parsing_invalid_dictionary_logs_error(
    caplog: pytest.LogCaptureFixture,
):
    """
    Attempting to parse an invalid dictionary which throws a ``TypeError``
    is suppressed and logs an error instead.

    Future refactoring should result in this test being binned.
    """

    error_msg = "There was an error when trying to parse the dictionary"
    with caplog.at_level(logging.INFO):
        result = apply._parse_aliases(None)  # type: ignore
        assert result is None
        assert error_msg in caplog.text


def test__formatting_dictionary_with_missing_key_logs_error(
    caplog: pytest.LogCaptureFixture,
):
    """
    Attempting to format a dict with a missing ``dictionary`` key returns
    the dict with the key set to an empty list.

    Future refactoring should result in this test being binned.
    """

    result = apply._format_dictionary({})
    assert result == {"dictionary": []}


def test__formatting_invalid_dictionary_logs_error(
    caplog: pytest.LogCaptureFixture,
):
    """
    Attempting to format an invalid dictionary which throws a ``TypeError``
    is suppressed and logs an error instead.

    Future refactoring should result in this test being binned.
    """

    error_msg = "There was an error when trying to format the dictionary"
    with caplog.at_level(logging.INFO):
        result = apply._format_dictionary(None)  # type: ignore
        assert result is None
        assert error_msg in caplog.text


def test__existing_fields_with_descriptions_can_be_updated(
    datadict_instance: apply.DataDict,
):
    """
    Existing dictionary fields with descriptions can be updated.
    """

    model_column = {"name": "field1", "description": "desc1"}
    model = {"name": "model1"}
    file_path = "path/to/file1.yml"
    apply._update_existing_field(
        datadict_instance.existing_fields,
        model_column,
        model,
        file_path,
    )

    expected = [
        {
            "name": "field1",
            "description": "desc1",
            "model": "model1",
            "file": "path/to/file1.yml",
        }
    ]
    assert datadict_instance.existing_fields == expected


def test__existing_fields_without_descriptions_can_be_updated(
    datadict_instance: apply.DataDict,
):
    """
    Existing dictionary fields without descriptions can be updated.
    """

    model_column = {"name": "field2"}
    model = {"name": "model2"}
    file_path = "path/to/file2.yml"
    apply._update_existing_field(
        datadict_instance.existing_fields,
        model_column,
        model,
        file_path,
    )

    expected = [
        {
            "name": "field2",
            "model": "model2",
            "file": "path/to/file2.yml",
        }
    ]
    assert datadict_instance.existing_fields == expected


def test__dictionary_can_be_iterated_with_updates(
    datadict_instance: apply.DataDict,
):
    """
    Dictionary updates can be applied iteratively.
    """

    model_yaml = {
        "models": [
            {
                "name": "model1",
                "columns": [{"name": "field1", "description": "old_desc"}],
            }
        ]
    }
    datadict_instance.dictionary_yml = {
        "dictionary": [{"name": "field1", "description": "new_desc"}]
    }
    updates = datadict_instance.iterate_dictionary_update(
        model_yaml, "path/to/model.yml"
    )

    assert updates["updated"]
    assert model_yaml["models"][0]["columns"][0]["description"] == "new_desc"


def test__dictionary_can_be_iterated_without_updates(
    datadict_instance: apply.DataDict,
):
    """
    Dictionary updates can be skipped iteratively.
    """

    model_yaml = {
        "models": [
            {
                "name": "model2",
                "columns": [{"name": "field2", "description": "desc2"}],
            }
        ]
    }
    datadict_instance.dictionary_yml = {
        "dictionary": [{"name": "field1", "description": "new_desc"}]
    }
    updates = datadict_instance.iterate_dictionary_update(
        model_yaml, "path/to/model.yml"
    )

    assert not updates["updated"]
    assert model_yaml["models"][0]["columns"][0]["description"] == "desc2"


def test__dictionary_metadata_can_be_collated(
    datadict_instance: apply.DataDict,
):
    """
    Metadata from existing fields can be collated.
    """

    existing_fields = [
        {"name": "field1", "model": "model1", "description": "desc1"},
        {"name": "field1", "model": "model2", "description": "desc2"},
        {"name": "field2", "model": "model1", "description": "desc3"},
        {"name": "field2", "model": "model2"},
    ]
    result = apply._collate_metadata(existing_fields)

    expected = [
        {
            "name": "field1",
            "description": "",
            "description_versions": ["desc1", "desc2"],
            "models": ["model1", "model2"],
        },
        {
            "name": "field2",
            "description": "desc3",
            "models": ["model1", "model2"],
        },
    ]
    assert result == expected


def test__dictionary_can_be_applied_to_a_model(
    temp_dir: pathlib.Path,
    datadict_instance: apply.DataDict,
):
    """
    A data dictionary can be applied to a model YAML file.
    """

    datadict_instance.dictionary_yml = {
        "dictionary": [{"name": "field1", "description": "new_desc"}]
    }
    model_yaml = {
        "models": [
            {
                "name": "test_model",
                "columns": [{"name": "field1", "description": "old_desc"}],
            }
        ]
    }
    model_yaml_file = temp_dir / "model_file.yml"
    with open(model_yaml_file, "w") as file:
        utils.YAML.dump(model_yaml, file)

    apply.apply_data_dictionary_to_file(
        str(model_yaml_file),
        datadict_instance.iterate_dictionary_update,
    )
    with open(model_yaml_file) as file:
        updated_yaml = utils.YAML.load(file)

    expected_yaml = {
        "models": [
            {
                "name": "test_model",
                "columns": [{"name": "field1", "description": "new_desc"}],
            }
        ]
    }
    assert updated_yaml == expected_yaml


def test__dictionary_is_not_applied_to_updated_model(
    caplog: pytest.LogCaptureFixture,
    temp_dir: pathlib.Path,
    datadict_instance: apply.DataDict,
):
    """
    A model YAML file is not changed if it is already up to date.
    """

    datadict_instance.dictionary_yml = {
        "dictionary": [{"name": "field1", "description": "desc"}]
    }
    model_yaml = {
        "models": [
            {
                "name": "test_model",
                "columns": [{"name": "field1", "description": "desc"}],
            }
        ]
    }
    model_yaml_file = temp_dir / "model_file.yml"
    info_msg = f"No updates found for file '{model_yaml_file}'"
    with open(model_yaml_file, "w") as file:
        utils.YAML.dump(model_yaml, file)

    with caplog.at_level(logging.INFO):
        apply.apply_data_dictionary_to_file(
            str(model_yaml_file),
            datadict_instance.iterate_dictionary_update,
        )
    with open(model_yaml_file) as file:
        updated_yaml = utils.YAML.load(file)

    assert updated_yaml == model_yaml
    assert info_msg in caplog.text


def test__applying_to_missing_file_logs_error(
    caplog: pytest.LogCaptureFixture,
    valid_model: ValidModel,
):
    """
    Applying the data dictionary to a missing file logs an error.

    Future refactoring should result in this test being binned.
    """

    def mock_dict_updater(_: dict, __: str) -> dict:
        raise FileNotFoundError

    file_path, _ = valid_model
    error_msg = f"File '{file_path}' not found."
    with caplog.at_level(logging.ERROR):
        apply.apply_data_dictionary_to_file(str(file_path), mock_dict_updater)
        assert error_msg in caplog.text


def test__applying_with_exception_logs_error(
    caplog: pytest.LogCaptureFixture,
    valid_model: ValidModel,
):
    """
    When applying the data dictionary raises an unhandled exception, the
    exception is logged.

    Future refactoring should result in this test being binned.
    """

    def mock_dict_updater(_: dict, __: str) -> dict:
        raise Exception("Something broke")

    file_path, _ = valid_model
    error_msg = f"Error processing file '{file_path}'. Error: Something broke"
    with caplog.at_level(logging.ERROR):
        apply.apply_data_dictionary_to_file(str(file_path), mock_dict_updater)
        assert error_msg in caplog.text


def test__dictionary_can_be_applied_to_multiple_models(
    temp_dir: pathlib.Path,
    datadict_instance: apply.DataDict,
):
    """
    A data dictionary can be applied to multiple model YAML files.
    """

    datadict_instance.dictionary_yml = {
        "dictionary": [{"name": "field1", "description": "new_desc"}]
    }
    model_yaml_file1 = os.path.join(temp_dir, "model_file1.yml")
    model_yaml_1 = {
        "models": [
            {
                "name": "test_model1",
                "columns": [{"name": "field1", "description": "old_desc"}],
            }
        ]
    }
    model_yaml_file2 = os.path.join(temp_dir, "model_file2.yml")
    model_yaml_2 = {
        "models": [
            {
                "name": "test_model2",
                "columns": [{"name": "field1", "description": "old_desc"}],
            }
        ]
    }
    with open(model_yaml_file1, "w") as file:
        utils.YAML.dump(model_yaml_1, file)
    with open(model_yaml_file2, "w") as file:
        utils.YAML.dump(model_yaml_2, file)
    apply.apply_data_dictionary_to_path(
        str(temp_dir),
        datadict_instance.iterate_dictionary_update,
    )
    with open(model_yaml_file1) as file:
        updated_yaml1 = utils.YAML.load(file)
    with open(model_yaml_file2) as file:
        updated_yaml2 = utils.YAML.load(file)

    expected_yaml1 = {
        "models": [
            {
                "name": "test_model1",
                "columns": [{"name": "field1", "description": "new_desc"}],
            }
        ]
    }
    expected_yaml2 = {
        "models": [
            {
                "name": "test_model2",
                "columns": [{"name": "field1", "description": "new_desc"}],
            }
        ]
    }
    assert updated_yaml1 == expected_yaml1
    assert updated_yaml2 == expected_yaml2


def test__applying_dictionary_to_missing_path_logs_error(
    caplog: pytest.LogCaptureFixture,
    datadict_instance: apply.DataDict,
):
    """
    Applying the data dictionary to a missing directory logs an error.
    """

    datadict_instance.dictionary_yml = {
        "dictionary": [{"name": "field1", "description": "new_desc"}]
    }

    missing_dir = "some/missing/dir"
    error_msg = f"Directory '{missing_dir}' doesn't exist or can't be found"
    with caplog.at_level(logging.ERROR):
        apply.apply_data_dictionary_to_path(
            missing_dir,
            datadict_instance.iterate_dictionary_update,
        )

    assert error_msg in caplog.text


def test__updating_model_adds_missing_description(
    caplog: pytest.LogCaptureFixture,
    temp_dir: pathlib.Path,
):
    """
    Applying a model update adds missing attributes to the model.
    """

    dictionary = {
        "dictionary": [
            {"name": "some_column", "description": "something awesome"}
        ]
    }
    dictionary_file = temp_dir / "datadictionary.yml"
    _yaml_dumps(dictionary, dictionary_file)
    datadict = apply.DataDict(dictionary_file)

    model_yaml = {
        "models": [{"name": "some_model", "columns": [{"name": "some_column"}]}]
    }
    model_yaml_file = temp_dir / "models.yml"
    _yaml_dumps(model_yaml, model_yaml_file)

    result = datadict.iterate_dictionary_update(
        model_yaml, str(model_yaml_file)
    )
    expected_result = {
        "updated": True,
        "model_yaml": {
            "models": [
                {
                    "name": "some_model",
                    "columns": [
                        {
                            "name": "some_column",
                            "description": "something awesome",
                        }
                    ],
                }
            ]
        },
    }

    assert result == expected_result


def test__updating_model_without_columns_logs_warning(
    caplog: pytest.LogCaptureFixture,
    temp_dir: pathlib.Path,
    datadict_instance: apply.DataDict,
):
    """
    Applying a model update on a model with no columns logs a warning.
    """

    model_yaml = {"models": [{"name": "model_without_columns"}]}
    model_yaml_file = temp_dir / "models.yml"
    with open(model_yaml_file, "w") as file:
        utils.YAML.dump(model_yaml, file)

    warning_msg = f"No columns found for model model_without_columns in '{model_yaml_file}'"
    with caplog.at_level(logging.WARNING):
        result = datadict_instance.iterate_dictionary_update(
            model_yaml, str(model_yaml_file)
        )

    assert result == {"updated": False}
    assert warning_msg in caplog.text


def test__missing_fields_can_be_collated(
    datadict_instance: apply.DataDict,
):
    """
    Missing dictionary fields can be collated.
    """

    datadict_instance.existing_fields = [
        {"name": "field3", "model": "model1", "description": "desc1"},
        {"name": "field3", "model": "model2", "description": "desc2"},
        {"name": "field4", "model": "model1", "description": "desc3"},
        {"name": "field4", "model": "model2"},
    ]

    datadict_instance.collate_output_dictionary()
    with open(datadict_instance.dictionary_path) as file:
        new_dict = utils.YAML.load(file)

    expected_missing_fields = [
        {
            "name": "field3",
            "description": "",
            "description_versions": ["desc1", "desc2"],
            "models": ["model1", "model2"],
        },
        {
            "name": "field4",
            "description": "desc3",
            "models": ["model1", "model2"],
        },
    ]
    assert new_dict["dictionary"] == expected_missing_fields


def test__collating_with_exception_logs_error(
    caplog: pytest.LogCaptureFixture,
    datadict_instance: apply.DataDict,
):
    """
    When collating the data dictionary raises an unhandled exception, the
    exception is logged.

    Future refactoring should result in this test being binned.
    """

    datadict_instance.dictionary_path = "something/broken"
    error_msg = f"There was a problem updating dictionary at '{datadict_instance.dictionary_path}'."
    with caplog.at_level(logging.ERROR):
        datadict_instance.collate_output_dictionary()

    assert error_msg in caplog.text
