import os
import pathlib

import ruamel.yaml

from dbt_datadict import utils


def test__valid_yaml_files_can_be_opened(
    temp_dir: pathlib.Path,
    yaml_obj: ruamel.yaml.YAML,
):
    """
    Valid YAML files can be opened and parsed correctly.
    """

    model_yaml_file = os.path.join(temp_dir, "model_file.yml")
    model_yaml = {
        "models": [
            {
                "name": "test_model",
                "columns": [{"name": "field1", "description": "old_desc"}],
            }
        ]
    }
    with open(model_yaml_file, "w") as file:
        yaml_obj.dump(model_yaml, file)
    result = utils.open_model_yml_file(model_yaml_file)

    assert result["status"] == "valid"
    assert isinstance(result["yaml"], dict)


def test__invalid_yaml_files_return_invalid_status(
    temp_dir: pathlib.Path,
    yaml_obj: ruamel.yaml.YAML,
):
    """
    Invalid YAML files return an invalid status and None for the YAML content.
    """

    invalid_model_yaml_file = os.path.join(temp_dir, "invalid_model_file.yml")
    with open(invalid_model_yaml_file, "w") as file:
        file.write("invalid_data:\n")
    result = utils.open_model_yml_file(invalid_model_yaml_file)

    assert result["status"] == "invalid"
    assert result["yaml"] is None


def test__models_can_be_validated_as_valid():
    """
    Models can be validated as valid.
    """

    valid_model_yaml = {
        "models": [
            {
                "name": "model1",
                "columns": [{"name": "column1", "description": "desc1"}],
            }
        ]
    }
    result = utils.check_valid_model_file(valid_model_yaml)

    assert result


def test__models_can_be_validated_as_invalid():
    """
    Models can be validated as invalid.
    """

    invalid_model_yaml = {"invalid_data": "data"}
    result = utils.check_valid_model_file(invalid_model_yaml)

    assert result is False


def test__model_yaml_files_can_be_output(
    temp_dir: pathlib.Path,
    yaml_obj: ruamel.yaml.YAML,
):
    model_yaml = {
        "models": [
            {
                "name": "test_model",
                "description": "Test Model",
                "columns": [
                    {"name": "col1", "description": "Column 1"},
                    {"name": "col2", "description": "Column 2"},
                ],
            }
        ]
    }
    test_file_path = str(temp_dir / "test_output_model.yaml")
    utils.output_model_file(yaml_obj, test_file_path, model_yaml, False)

    assert os.path.exists(test_file_path)

    with open(test_file_path) as f:
        loaded_yaml = yaml_obj.load(f)

    assert loaded_yaml == model_yaml


def test__dictionary_files_can_be_listed(
    temp_dir: pathlib.Path,
):
    """
    Dictionary files can be listed.
    """

    extensions = [".yml", ".yaml"]
    yaml_files = [
        "file1.yaml",
        "file2.yml",
        "subdir/file3.yaml",
        "subdir/file4.yml",
        "subdir/subsubdir/file5.yaml",
        "subdir/subsubdir/file6.yml",
        "non_yaml_file.txt",
    ]
    for file in yaml_files:
        file_path = temp_dir / file
        file_path.parent.mkdir(exist_ok=True, parents=True)
        file_path.touch(exist_ok=True)
        file_path.write_text("Sample YAML content")

    yaml_files_list: list = utils.list_directory_files(  # type: ignore
        str(temp_dir),
        extensions,
    )

    expected_yaml_files = [
        str(temp_dir / file)
        for file in yaml_files_list
        if file.endswith(tuple(extensions))
    ]
    assert yaml_files_list.sort() == expected_yaml_files.sort()


def test__model_files_can_be_sorted():
    input_dict = {
        "version": 2,
        "models": [
            {
                "name": "dmn_clients",
                "columns": [
                    {"name": "updated_at", "description": ""},
                    {
                        "name": "client_uuid",
                        "description": "Unique identifier for the client",
                        "tests": ["unique", "not_null"],
                    },
                    {
                        "name": "name",
                        "description": "Name of the client",
                        "tests": ["not_null"],
                    },
                    {
                        "name": "code",
                        "description": "Code used to uniquely identify the client",
                        "tests": ["not_null"],
                    },
                    {
                        "name": "board_name",
                        "description": "Name of the board in monday.com",
                    },
                    {
                        "name": "status",
                        "description": "Status of the client",
                        "tests": ["not_null"],
                    },
                ],
            },
            {
                "name": "dmn_stories",
                "columns": [
                    {"name": "valid_from", "description": ""},
                    {"name": "story_id", "description": ""},
                    {"name": "name", "description": ""},
                    {"name": "client_uuid", "description": ""},
                    {"name": "client_name", "description": ""},
                ],
            },
        ],
    }
    sorted_output = utils.sort_model_file(input_dict)

    expected_output = {
        "version": 2,
        "models": [
            {
                "name": "dmn_clients",
                "columns": [
                    {
                        "name": "board_name",
                        "description": "Name of the board in monday.com",
                    },
                    {
                        "name": "client_uuid",
                        "description": "Unique identifier for the client",
                        "tests": ["unique", "not_null"],
                    },
                    {
                        "name": "code",
                        "description": "Code used to uniquely identify the client",
                        "tests": ["not_null"],
                    },
                    {
                        "name": "name",
                        "description": "Name of the client",
                        "tests": ["not_null"],
                    },
                    {
                        "name": "status",
                        "description": "Status of the client",
                        "tests": ["not_null"],
                    },
                    {"name": "updated_at", "description": ""},
                ],
            },
            {
                "name": "dmn_stories",
                "columns": [
                    {"name": "client_name", "description": ""},
                    {"name": "client_uuid", "description": ""},
                    {"name": "name", "description": ""},
                    {"name": "story_id", "description": ""},
                    {"name": "valid_from", "description": ""},
                ],
            },
        ],
    }
    assert sorted_output == expected_output
