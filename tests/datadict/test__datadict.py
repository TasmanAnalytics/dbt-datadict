import os
import pathlib

import pytest

import datadict


@pytest.fixture(scope="function")
def dictionary_file(temp_dir: pathlib.Path) -> pathlib.Path:
    """
    A temporary dictionary YAML file.
    """

    file_path = temp_dir / "test_dictionary.yml"
    file_path.write_text("dictionary:\n")

    return file_path


@pytest.fixture(scope="function")
def datadict_instance(dictionary_file: pathlib.Path) -> datadict.datadict:
    """
    A DataDict instance in the temporary directory.
    """

    return datadict.datadict(str(dictionary_file))


def test__dictionary_can_be_loaded(datadict_instance: datadict.datadict):
    """
    A dictionary can be loaded correctly.
    """

    loaded_dict = datadict_instance._load_dictionary()

    assert isinstance(loaded_dict, dict)


def test__dictionary_cannot_be_loaded_if_not_exists(
    temp_dir: pathlib.Path,
    datadict_instance: datadict.datadict,
):
    """
    A dictionary can be loaded correctly.
    """

    non_existent_dict_file = temp_dir / "non_existent_dict.yml"
    datadict_instance.dictionary_path = str(non_existent_dict_file)

    with pytest.raises(FileNotFoundError):
        datadict_instance._load_dictionary()


def test__dictionary_can_be_created(
    temp_dir: pathlib.Path,
    datadict_instance: datadict.datadict,
):
    """
    A new dictionary can be created.
    """

    new_dict_file = temp_dir / "new_dict.yml"
    datadict_instance.dictionary_path = str(new_dict_file)
    created_dict = datadict_instance._create_dictinary()

    assert isinstance(created_dict, dict)
    assert new_dict_file.exists()


def test__dictionary_can_be_updated(datadict_instance: datadict.datadict):
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
    formatted_yaml = datadict_instance._format_dictionary(original)

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


def test__dictionary_can_be_parsed_without_aliases(datadict_instance: datadict.datadict):
    """
    A dictionary can be parsed correctly without aliases.
    """

    dictionary = {"dictionary": [{"name": "field1"}, {"name": "field2"}]}
    result = datadict_instance._parse_aliases(dictionary)

    assert result == ["field1", "field2"]


def test__dictionary_can_be_parsed_with_aliases(datadict_instance: datadict.datadict):
    """
    A dictionary can be parsed correctly with aliases.
    """

    test_dictionary = {
        "dictionary": [
            {"name": "field1", "aliases": ["f1", "alias1"]},
            {"name": "field2"},
        ]
    }
    result = datadict_instance._parse_aliases(test_dictionary)

    assert result == ["field1", "f1", "alias1", "field2"]


def test__dictionary_items_can_be_inserted(datadict_instance: datadict.datadict):
    """
    A dictionary item can be inserted.
    """

    test_dict = {"key1": "value1", "key3": "value3"}
    result_dict = datadict_instance._insert_dict_item(
        test_dict, "key2", "value2", 1
    )

    assert result_dict == {"key1": "value1", "key2": "value2", "key3": "value3"}


def test__existing_fields_with_descriptions_can_be_updated(
    datadict_instance: datadict.datadict,
):
    """
    Existing dictionary fields with descriptions can be updated.
    """

    model_column = {"name": "field1", "description": "desc1"}
    model = {"name": "model1"}
    file_path = "path/to/file1.yml"
    datadict_instance._update_existing_field(model_column, model, file_path)

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
    datadict_instance: datadict.datadict,
):
    """
    Existing dictionary fields without descriptions can be updated.
    """

    model_column = {"name": "field2"}
    model = {"name": "model2"}
    file_path = "path/to/file2.yml"
    datadict_instance._update_existing_field(model_column, model, file_path)

    expected = [
        {
            "name": "field2",
            "model": "model2",
            "file": "path/to/file2.yml",
        }
    ]
    assert datadict_instance.existing_fields == expected


def test__dictionary_can_be_iterated_with_updates(
    datadict_instance: datadict.datadict,
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
    updates = datadict_instance._iterate_dictionary_update(
        model_yaml, "path/to/model.yml"
    )

    assert updates["updated"]
    assert model_yaml["models"][0]["columns"][0]["description"] == "new_desc"


def test__dictionary_can_be_iterated_without_updates(
    datadict_instance: datadict.datadict,
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
    updates = datadict_instance._iterate_dictionary_update(
        model_yaml, "path/to/model.yml"
    )

    assert not updates["updated"]
    assert model_yaml["models"][0]["columns"][0]["description"] == "desc2"


def test__dictionary_metadata_can_be_collated(
    datadict_instance: datadict.datadict,
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
    result = datadict_instance._collate_metadata(existing_fields)

    expected = [
        {
            "name": "field1",
            "description": "",
            "description_versions": ["desc1", "desc2"],
            "models": ["model1", "model2"],
        },
        {"name": "field2", "description": "desc3", "models": ["model1", "model2"]},
    ]
    assert result == expected


def test__dictionary_can_be_applied_to_a_model(
    temp_dir: pathlib.Path,
    datadict_instance: datadict.datadict,
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
        datadict_instance.yaml.dump(model_yaml, file)

    datadict_instance.apply_data_dictionary_to_file(str(model_yaml_file))
    with open(model_yaml_file, "r") as file:
        updated_yaml = datadict_instance.yaml.load(file)

    expected_yaml = {
        "models": [
            {
                "name": "test_model",
                "columns": [{"name": "field1", "description": "new_desc"}],
            }
        ]
    }
    assert updated_yaml == expected_yaml


def test__dictionary_can_be_applied_to_multiple_models(
    temp_dir: pathlib.Path,
    datadict_instance: datadict.datadict,
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
        datadict_instance.yaml.dump(model_yaml_1, file)
    with open(model_yaml_file2, "w") as file:
        datadict_instance.yaml.dump(model_yaml_2, file)
    datadict_instance.apply_data_dictionary_to_path(str(temp_dir))
    with open(model_yaml_file1, "r") as file:
        updated_yaml1 = datadict_instance.yaml.load(file)
    with open(model_yaml_file2, "r") as file:
        updated_yaml2 = datadict_instance.yaml.load(file)

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


def test__missing_fields_can_be_collated(
    datadict_instance: datadict.datadict,
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
    with open(datadict_instance.dictionary_path, "r") as file:
        new_dict = datadict_instance.yaml.load(file)

    expected_missing_fields = [
        {
            "name": "field3",
            "description": "",
            "description_versions": ["desc1", "desc2"],
            "models": ["model1", "model2"],
        },
        {"name": "field4", "description": "desc3", "models": ["model1", "model2"]},
    ]
    assert new_dict["dictionary"] == expected_missing_fields
