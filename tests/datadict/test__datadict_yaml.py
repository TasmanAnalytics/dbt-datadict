from datadict import datadict_yaml


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
