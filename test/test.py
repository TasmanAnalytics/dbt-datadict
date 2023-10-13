import unittest
import os
import tempfile
import datadict
import shutil
import ruamel.yaml
from datadict import datadict_helpers
from datadict import datadict_yaml


class TestDataDict(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to store the test files
        self.temp_dir = tempfile.mkdtemp()

        # Create a test dictionary YAML file
        self.dictionary_file = os.path.join(self.temp_dir, "test_dictionary.yml")
        with open(self.dictionary_file, "w") as file:
            file.write("dictionary:\n")

        # Create an instance of the datadict class with the test dictionary
        self.datadict_instance = datadict.datadict(self.dictionary_file)

    def tearDown(self):
        # Remove the temporary directory and its contents after the test
        shutil.rmtree(self.temp_dir)

    def test_load_dictionary(self):
        # Test loading an existing dictionary
        loaded_dict = self.datadict_instance._load_dictionary()
        self.assertIsInstance(loaded_dict, dict)

        # Test loading a non-existent dictionary
        non_existent_dict_file = os.path.join(self.temp_dir, "non_existent_dict.yml")
        with self.assertRaises(FileNotFoundError):
            self.datadict_instance.dictionary_path = non_existent_dict_file
            self.datadict_instance._load_dictionary()

    def test_create_dictionary(self):
        # Test creating a new dictionary
        new_dict_file = os.path.join(self.temp_dir, "new_dict.yml")
        self.datadict_instance.dictionary_path = new_dict_file
        created_dict = self.datadict_instance._create_dictinary()
        self.assertIsInstance(created_dict, dict)
        self.assertTrue(os.path.exists(new_dict_file))

    def test_format_dictionary(self):
        # Test formatting an existing dictionary
        original_yaml = {
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
        expected_yaml = {
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
        formatted_yaml = self.datadict_instance._format_dictionary(original_yaml)
        self.assertEqual(expected_yaml, formatted_yaml)

    def test_parse_aliases(self):
        # Test parsing dictionary with no aliases
        test_dictionary = {"dictionary": [{"name": "field1"}, {"name": "field2"}]}
        result = self.datadict_instance._parse_aliases(test_dictionary)
        self.assertEqual(result, ["field1", "field2"])

        # Test parsing dictionary with aliases
        test_dictionary = {
            "dictionary": [
                {"name": "field1", "aliases": ["f1", "alias1"]},
                {"name": "field2"},
            ]
        }
        result = self.datadict_instance._parse_aliases(test_dictionary)
        self.assertEqual(result, ["field1", "f1", "alias1", "field2"])

    def test_insert_dict_item(self):
        test_dict = {"key1": "value1", "key3": "value3"}
        result_dict = self.datadict_instance._insert_dict_item(
            test_dict, "key2", "value2", 1
        )
        expected_dict = {"key1": "value1", "key2": "value2", "key3": "value3"}
        self.assertEqual(result_dict, expected_dict)

    def test_update_existing_field(self):
        # Test updating existing field with description
        model_column = {"name": "field1", "description": "desc1"}
        model = {"name": "model1"}
        file_path = "path/to/file1.yml"
        self.datadict_instance._update_existing_field(model_column, model, file_path)
        self.assertEqual(
            self.datadict_instance.existing_fields,
            [
                {
                    "name": "field1",
                    "description": "desc1",
                    "model": "model1",
                    "file": "path/to/file1.yml",
                }
            ],
        )

        # Test updating existing field without description
        model_column = {"name": "field2"}
        model = {"name": "model2"}
        file_path = "path/to/file2.yml"
        self.datadict_instance._update_existing_field(model_column, model, file_path)
        self.assertEqual(
            self.datadict_instance.existing_fields,
            [
                {
                    "name": "field1",
                    "description": "desc1",
                    "model": "model1",
                    "file": "path/to/file1.yml",
                },
                {"name": "field2", "model": "model2", "file": "path/to/file2.yml"},
            ],
        )

    def test_iterate_dictionary_update(self):
        # Test iterating through model YAML and updating descriptions
        model_yaml = {
            "models": [
                {
                    "name": "model1",
                    "columns": [{"name": "field1", "description": "old_desc"}],
                }
            ]
        }
        self.datadict_instance.dictionary_yml = {
            "dictionary": [{"name": "field1", "description": "new_desc"}]
        }
        updates = self.datadict_instance._iterate_dictionary_update(
            model_yaml, "path/to/model.yml"
        )
        self.assertTrue(updates["updated"])
        self.assertEqual(
            model_yaml["models"][0]["columns"][0]["description"], "new_desc"
        )

        # Test iterating through model YAML without updates
        model_yaml = {
            "models": [
                {
                    "name": "model2",
                    "columns": [{"name": "field2", "description": "desc2"}],
                }
            ]
        }
        self.datadict_instance.dictionary_yml = {
            "dictionary": [{"name": "field1", "description": "new_desc"}]
        }
        updates = self.datadict_instance._iterate_dictionary_update(
            model_yaml, "path/to/model.yml"
        )
        self.assertFalse(updates["updated"])
        self.assertEqual(model_yaml["models"][0]["columns"][0]["description"], "desc2")

    def test_collate_metadata(self):
        # Test collating metadata from existing fields
        existing_fields = [
            {"name": "field1", "model": "model1", "description": "desc1"},
            {"name": "field1", "model": "model2", "description": "desc2"},
            {"name": "field2", "model": "model1", "description": "desc3"},
            {"name": "field2", "model": "model2"},
        ]
        result = self.datadict_instance._collate_metadata(existing_fields)
        expected_result = [
            {
                "name": "field1",
                "description": "",
                "description_versions": ["desc1", "desc2"],
                "models": ["model1", "model2"],
            },
            {"name": "field2", "description": "desc3", "models": ["model1", "model2"]},
        ]
        self.assertEqual(result, expected_result)

    def test_apply_data_dictionary_to_file(self):
        # Test applying data dictionary to valid model file
        self.datadict_instance.dictionary_yml = {
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
        model_yaml_file = os.path.join(self.temp_dir, "model_file.yml")
        with open(model_yaml_file, "w") as file:
            self.datadict_instance.yaml.dump(model_yaml, file)
        self.datadict_instance.apply_data_dictionary_to_file(model_yaml_file)
        with open(model_yaml_file, "r") as file:
            updated_yaml = self.datadict_instance.yaml.load(file)
        expected_yaml = {
            "models": [
                {
                    "name": "test_model",
                    "columns": [{"name": "field1", "description": "new_desc"}],
                }
            ]
        }
        self.assertEqual(updated_yaml, expected_yaml)

    def test_apply_data_dictionary_to_path(self):
        # Test applying data dictionary to files in a directory
        self.datadict_instance.dictionary_yml = {
            "dictionary": [{"name": "field1", "description": "new_desc"}]
        }
        model_yaml_file1 = os.path.join(self.temp_dir, "model_file1.yml")
        model_yaml_1 = {
            "models": [
                {
                    "name": "test_model1",
                    "columns": [{"name": "field1", "description": "old_desc"}],
                }
            ]
        }
        model_yaml_file2 = os.path.join(self.temp_dir, "model_file2.yml")
        model_yaml_2 = {
            "models": [
                {
                    "name": "test_model2",
                    "columns": [{"name": "field1", "description": "old_desc"}],
                }
            ]
        }
        with open(model_yaml_file1, "w") as file:
            self.datadict_instance.yaml.dump(model_yaml_1, file)
        with open(model_yaml_file2, "w") as file:
            self.datadict_instance.yaml.dump(model_yaml_2, file)
        self.datadict_instance.apply_data_dictionary_to_path(self.temp_dir)
        with open(model_yaml_file1, "r") as file:
            updated_yaml1 = self.datadict_instance.yaml.load(file)
        with open(model_yaml_file2, "r") as file:
            updated_yaml2 = self.datadict_instance.yaml.load(file)
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
        self.assertEqual(updated_yaml1, expected_yaml1)
        self.assertEqual(updated_yaml2, expected_yaml2)

    def test_collate_output_dictionary(self):
        # Test loading missing fields with existing fields
        self.datadict_instance.existing_fields = [
            {"name": "field3", "model": "model1", "description": "desc1"},
            {"name": "field3", "model": "model2", "description": "desc2"},
            {"name": "field4", "model": "model1", "description": "desc3"},
            {"name": "field4", "model": "model2"},
        ]

        self.datadict_instance.collate_output_dictionary()

        with open(self.datadict_instance.dictionary_path, "r") as file:
            new_dict = self.datadict_instance.yaml.load(file)
        expected_missing_fields = [
            {
                "name": "field3",
                "description": "",
                "description_versions": ["desc1", "desc2"],
                "models": ["model1", "model2"],
            },
            {"name": "field4", "description": "desc3", "models": ["model1", "model2"]},
        ]

        self.assertEqual(new_dict["dictionary"], expected_missing_fields)


class TestHelpers(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to store the test files
        self.temp_dir = tempfile.mkdtemp()
        self.yaml_obj = ruamel.yaml.YAML()

    def tearDown(self):
        # Remove the temporary directory and its contents after the test
        shutil.rmtree(self.temp_dir)

    def test_open_model_yml_file(self):
        # Test opening a valid model YAML file
        model_yaml_file = os.path.join(self.temp_dir, "model_file.yml")
        model_yaml = {
            "models": [
                {
                    "name": "test_model",
                    "columns": [{"name": "field1", "description": "old_desc"}],
                }
            ]
        }
        with open(model_yaml_file, "w") as file:
            self.yaml_obj.dump(model_yaml, file)
        result = datadict_helpers.open_model_yml_file(self.yaml_obj, model_yaml_file)
        self.assertTrue(result["status"] == "valid")
        self.assertIsInstance(result["yaml"], dict)

        # Test opening an invalid model YAML file
        invalid_model_yaml_file = os.path.join(self.temp_dir, "invalid_model_file.yml")
        with open(invalid_model_yaml_file, "w") as file:
            file.write("invalid_data:\n")
        result = datadict_helpers.open_model_yml_file(
            self.yaml_obj, invalid_model_yaml_file
        )
        self.assertTrue(result["status"] == "invalid")
        self.assertIsNone(result["yaml"])

    def test_check_valid_model_file(self):
        # Test checking a valid model YAML data
        valid_model_yaml = {
            "models": [
                {
                    "name": "model1",
                    "columns": [{"name": "column1", "description": "desc1"}],
                }
            ]
        }
        result = datadict_helpers.check_valid_model_file(valid_model_yaml)
        self.assertTrue(result)

        # Test checking an invalid model YAML data
        invalid_model_yaml = {"invalid_data": "data"}
        result = datadict_helpers.check_valid_model_file(invalid_model_yaml)
        self.assertFalse(result)

    def test_output_model_file(self):
        # Prepare test data
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
        test_file_path = "test_output_model.yaml"
        try:
            datadict_helpers.output_model_file(
                self.yaml_obj, test_file_path, model_yaml, False
            )
            self.assertTrue(os.path.exists(test_file_path))
            with open(test_file_path, "r") as f:
                loaded_yaml = self.yaml_obj.load(f)
            self.assertEqual(loaded_yaml, model_yaml)

        finally:
            if os.path.exists(test_file_path):
                os.remove(test_file_path)

    def test_list_directory_files(self):
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
            file_path = os.path.join(self.temp_dir, file)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write("Sample YAML content")
        # Call the function to get the list of YAML files in the temporary directory
        yaml_files_list = datadict_helpers.list_directory_files(
            self.temp_dir, extensions
        )

        # Assert that the function returns the correct list of YAML files
        expected_yaml_files = [
            os.path.join(self.temp_dir, "file1.yaml"),
            os.path.join(self.temp_dir, "file2.yml"),
            os.path.join(self.temp_dir, "subdir/file3.yaml"),
            os.path.join(self.temp_dir, "subdir/file4.yml"),
            os.path.join(self.temp_dir, "subdir/subsubdir/file5.yaml"),
            os.path.join(self.temp_dir, "subdir/subsubdir/file6.yml"),
        ]
        self.assertCountEqual(yaml_files_list, expected_yaml_files)

    def test_sort_model_file(self):
        # Input dictionary with unsorted models and columns
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

        # Expected output dictionary with sorted models and columns
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

        # Call the function to sort the model file
        sorted_output = datadict_helpers.sort_model_file(input_dict)

        # Compare the actual output with the expected output
        self.assertEqual(sorted_output, expected_output)


class TestYaml(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to store the test files
        self.temp_dir = tempfile.mkdtemp()
        self.yaml_obj = ruamel.yaml.YAML()

    def tearDown(self):
        # Remove the temporary directory and its contents after the test
        shutil.rmtree(self.temp_dir)

    def test_combine_column_lists_no_missing_columns(self):
        # Test when there are no missing columns
        current_yml = {
            "name": "Model1",
            "columns": [
                {"name": "Column1", "type": "int"},
                {"name": "Column2", "type": "str"},
            ],
        }
        expected_yml = {
            "columns": [
                {"name": "Column1", "type": "int"},
                {"name": "Column2", "type": "str"},
            ]
        }
        result = datadict_yaml.combine_column_lists(current_yml, expected_yml)
        self.assertEqual(result["updated"], False)
        self.assertDictEqual(result["yaml"], current_yml)

    def test_combine_column_lists_missing_columns(self):
        # Test when there are missing columns
        current_yml = {
            "name": "Model1",
            "columns": [
                {"name": "Column1", "type": "int"},
            ],
        }
        expected_yml = {
            "columns": [
                {"name": "Column1", "type": "int"},
                {"name": "Column2", "type": "str"},
            ]
        }
        result = datadict_yaml.combine_column_lists(current_yml, expected_yml)
        self.assertEqual(result["updated"], True)
        self.assertIn({"name": "Column2", "type": "str"}, result["yaml"]["columns"])

    def test_combine_column_lists_additional_columns(self):
        # Test when there are additional columns
        current_yml = {
            "name": "Model1",
            "columns": [
                {"name": "Column1", "type": "int"},
                {"name": "Column2", "type": "str"},
            ],
        }
        expected_yml = {
            "name": "Model1",
            "columns": [{"name": "Column1", "type": "int"}],
        }
        result = datadict_yaml.combine_column_lists(current_yml, expected_yml)
        self.assertEqual(result["updated"], True)
        self.assertDictEqual(result["yaml"], expected_yml)

    def test_combine_column_lists_empty_current_yml(self):
        # Test when current_yml has no columns initially
        current_yml = {"name": "Model1"}
        expected_yml = {
            "columns": [
                {"name": "Column1", "type": "int"},
            ]
        }
        result = datadict_yaml.combine_column_lists(current_yml, expected_yml)
        self.assertEqual(result["updated"], True)
        self.assertIn({"name": "Column1", "type": "int"}, result["yaml"]["columns"])


if __name__ == "__main__":
    unittest.main()
