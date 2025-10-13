import logging
import os
from collections.abc import Hashable
from typing import Any

import ruamel.yaml

YAML = ruamel.yaml.YAML()
YAML.preserve_quotes = True
YAML.indent(mapping=2, sequence=4, offset=2)
YAML.width = 200


def insert_dict_item(
    dictionary: dict,
    key: Hashable,
    value: Any,
    index: int,
) -> dict:
    """
    Return a new dictionary with the specified key-value pair inserted at
    the given index.
    """

    keys = list(dictionary.keys())
    values = list(dictionary.values())
    keys.insert(index, key)
    values.insert(index, value)

    return dict(zip(keys, values))


def add_spaces_between_cols(file):
    """
    Add spaces between columns in a YAML file.

    This function reads a YAML file and inserts newlines between the columns that start with '- name:'.
    It then writes the modified content back to the same file.

    Parameters:
        file (str): The path to the YAML file to be processed.

    Returns:
        None
    """
    with open(file) as f:
        yaml = f.read()
    replaced = yaml.replace("dictionary:\n\n", "dictionary:\n").replace(
        "  - name:", "\n  - name:"
    )
    with open(file, "w") as f:
        f.write(replaced)


def open_model_yml_file(file_path) -> dict:
    """
    Open and load a model YAML file for processing.

    This private method is used to open and load a YAML file from the provided file path. The function
    attempts to read and parse the file using the YAML parser. If the YAML data represents a valid model,
    it returns a dictionary with the status as "valid" and the loaded YAML data. Otherwise, it logs a
    message indicating that the file was skipped and returns a dictionary with the status as "invalid".

    Parameters:
        file_path (str): The path to the YAML file to be opened and loaded.

    Returns:
        dict: A dictionary with the keys "status" and "yaml". The "status" key will be either "valid" or "invalid".
            The "yaml" key will contain the loaded YAML data if valid, otherwise, it will contain None.
    """
    with open(file_path, "r+") as file:
        yaml = YAML.load(file)
        if check_valid_model_file(yaml):
            return {"status": "valid", "yaml": yaml}
        return {"status": "invalid", "yaml": None}


def check_valid_model_file(model_yaml) -> bool:
    """
    Check if the parsed YAML data represents a valid model.

    This private method is used to check whether the parsed YAML data contains the required 'models'
    key, indicating that it represents a valid model file.

    Parameters:
        yaml (dict): The parsed YAML data.

    Returns:
        bool: True if the YAML data contains the required 'models' key, False otherwise.
    """
    try:
        _ = model_yaml["models"]
        return True
    except KeyError:
        return False


def output_model_file(yaml_obj, file_path, model_yaml, sort) -> None:
    """
    Output the updated model YAML data to a file.

    This private method is used to write the updated model YAML data to a file specified by the 'file_path'.
    The function takes the 'model_yaml' data as input and writes it to the file using the YAML serializer.

    Parameters:
        file_path (str): The path to the file where the updated model YAML should be written.
        model_yaml (dict): The updated model YAML data to be written to the file.

    Returns:
        None
    """
    if sort:
        output_yaml = sort_model_file(model_yaml)
        logging.info(f"File '{file_path}' has been sorted")
    else:
        output_yaml = model_yaml
    with open(file_path, "w") as file:
        yaml_obj.dump(output_yaml, file)
        logging.info(f"Updated model file '{file_path}'")


def list_directory_files(directory, extensions) -> dict:
    """
    Lists all files with the provided extensions in the specified directory and its subdirectories.

    This function recursively searches the provided 'directory' for files found with the supplied extensions.
    It returns a list containing the absolute file paths of all the found files.

    Parameters:
        directory (str): The path to the directory to search for files.
        extensions (list): A list of extensions to check for.

    Returns:
        list: A list containing absolute file paths of YAML files in the specified directory and its subdirectories.
    """
    try:
        files_list = []
        if os.path.exists(directory) and os.path.isdir(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(tuple(extensions)):
                        files_list.append(os.path.join(root, file))
            logging.info(
                f"Found {len(files_list)} files in the directory '{directory}' with extensions: {', '.join(extensions)}"
            )
        else:
            logging.error(f"Directory '{directory}' doesn't existing.")
        return files_list

    except Exception as e:
        logging.error(
            f"Issues encountered when trying to search directory for yaml files: {e}"
        )


def sort_model_file(file_yaml) -> dict:
    """
    Sorts the dictionary of models by the column names within each model alphabetically.

    This function takes a dictionary containing model information, where each model has a list of columns.
    The function sorts the columns within each model alphabetically based on their 'name' key.
    Additionally, the function sorts the models themselves alphabetically based on their 'name' key.

    Parameters:
        file_yaml (dict): The dictionary containing model information.

    Returns:
        dict: The sorted dictionary with models and their columns sorted alphabetically by their names.
    """

    # Sort the columns within each model alphabetically
    for model in file_yaml["models"]:
        if "columns" in model:
            model["columns"] = sorted(
                model["columns"], key=lambda col: col["name"]
            )

    # Sort the models by name
    file_yaml["models"] = sorted(
        file_yaml["models"], key=lambda model: model["name"]
    )

    return file_yaml
