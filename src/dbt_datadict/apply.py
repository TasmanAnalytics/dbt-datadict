import logging
import os
import pathlib
from collections.abc import Callable

from dbt_datadict import utils


def load_or_create_dictionary(dictionary_path: str) -> dict:
    """
    Return a dictionary from a specified path.

    If the dictionary file does not exist, create a new dictionary with an
    empty list, but only if the directory exists.
    """

    dict_path = pathlib.Path(dictionary_path)
    if dict_path.exists() and dict_path.is_file():
        logging.info(f"Loading dictionary from '{dict_path.absolute()}'")
        return utils.YAML.load(dict_path.read_text())

    base_yaml = {"dictionary": []}
    try:
        utils.YAML.dump(base_yaml, dict_path)
        logging.info(
            f"The file '{dict_path.absolute()}' was successfully created."
        )
        return base_yaml
    except FileNotFoundError as err:
        logging.error(
            f"An error occurred while creating the file '{dict_path.absolute()}'. Check the directory exists."
        )
        raise err


def _parse_aliases(dictionary: dict) -> list | None:
    """
    Parse dictionary data to extract field names and their aliases.
    """

    try:
        values = []
        if dictionary["dictionary"] is None:
            return values
        for dict_column in dictionary["dictionary"]:
            values.append(dict_column["name"])
            try:
                for alias in dict_column["aliases"]:
                    values.append(alias)
            except:  # noqa: S110
                pass
        return values
    except TypeError:
        logging.info("There was an error when trying to parse the dictionary")


def _format_dictionary(dictionary_yml: dict) -> dict | None:
    """
    Format the dictionary data to ensure consistent structure.

    This ensures that each field in the `dictionary` key contains
    `description` and `aliases` keys. If any field is missing these keys,
    they will be added with appropriate default values.
    """

    try:
        if "dictionary" in dictionary_yml:
            if dictionary_yml["dictionary"] is not None:
                for field_num, field in enumerate(dictionary_yml["dictionary"]):
                    if "description" not in field:
                        dictionary_yml["dictionary"][field_num][
                            "description"
                        ] = ""
                    if "aliases" not in field:
                        dictionary_yml["dictionary"][field_num]["aliases"] = []
        else:
            dictionary_yml["dictionary"] = []
        return dictionary_yml
    except TypeError:
        logging.info("There was an error when trying to format the dictionary")


def _collate_metadata(existing_fields: list[dict]) -> list:
    """
    Collates metadata from existing field list.

    For each unique field name, collect unique models and non-empty
    descriptions associated with the field.
    """

    metadata = {}
    result = []

    # extract metadata from existing field list
    for field in existing_fields:
        name = field["name"]
        model = field["model"]
        description = field.get("description", "")

        if name not in metadata:
            metadata[name] = {
                "description_versions": [description],
                "description": description,
                "models": [model],
            }
        else:
            metadata[name]["description_versions"].append(description)
            metadata[name]["models"].append(model)

    # summarise metadata
    for name, info in metadata.items():
        versions = list(
            set(
                [
                    version
                    for version in info["description_versions"]
                    if version != ""
                ]
            )
        )
        versions.sort()
        models = list(set(info["models"]))
        models.sort()
        if len(versions) > 1:
            result.append(
                {
                    "name": name,
                    "description": "",
                    "description_versions": versions,
                    "models": models,
                }
            )
        else:
            result.append(
                {
                    "name": name,
                    "description": info["description"],
                    "models": models,
                }
            )

    # return field list sorted by name
    return sorted(result, key=lambda d: d["name"])


def apply_data_dictionary_to_file(
    file_path: str,
    # Taking a callable is a short-term solution during refactoring and
    # will be replaced with a more structured approach in the future
    dictionary_updater: Callable[[dict, str], dict],
) -> None:
    """
    Apply the data dictionary updates to the specified model YAML file.
    """

    logging.info(f"Checking file '{file_path}'...")
    model_yaml = utils.open_model_yml_file(file_path)
    if model_yaml["status"] == "valid":
        try:
            updates = dictionary_updater(model_yaml["yaml"], file_path)
            if updates["updated"]:
                utils.output_model_file(
                    utils.YAML, file_path, updates["model_yaml"], False
                )
                logging.info(f"File {file_path} has been updated")
            else:
                logging.info(f"No updates found for file '{file_path}'")

        except FileNotFoundError:
            logging.error(f"File '{file_path}' not found.")
        except Exception as e:
            logging.error(f"Error processing file '{file_path}'. Error: {e}")
    else:
        logging.info(
            f"File '{file_path}' contains no models and has been skipped."
        )


def apply_data_dictionary_to_path(
    directory: str,
    # Taking a callable is a short-term solution during refactoring and
    # will be replaced with a more structured approach in the future
    dictionary_updater: Callable[[dict, str], dict],
) -> None:
    """
    Apply the data dictionary updates to all model YAML files in the
    specified directory and its subdirectories.
    """

    if os.path.exists(directory) and os.path.isdir(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".yaml") or file.endswith(".yml"):
                    file_path = os.path.join(root, file)
                    apply_data_dictionary_to_file(file_path, dictionary_updater)
    else:
        logging.error(
            f"Directory '{directory}' doesn't exist or can't be found"
        )


def _update_existing_field(
    existing_fields: list[dict],
    model_column: dict,
    model: dict,
    file_path: str,
) -> None:
    """
    Update the list of existing fields with model column details.
    """

    if "description" in model_column:
        existing_fields.append(
            {
                "name": model_column["name"],
                "description": model_column["description"],
                "model": model["name"],
                "file": file_path,
            }
        )
    else:
        existing_fields.append(
            {
                "name": model_column["name"],
                "model": model["name"],
                "file": file_path,
            }
        )


class DataDict:
    def __init__(self, dictionary_file_path) -> None:
        self.dictionary_path = dictionary_file_path
        self.dictionary_yml = _format_dictionary(
            load_or_create_dictionary(dictionary_file_path)
        )
        self.dictionary_items = _parse_aliases(self.dictionary_yml)
        self.existing_fields = []
        self.missing_fields = []

    def iterate_dictionary_update(  # noqa: PLR0912
        self,
        model_yaml: dict,
        file_path: str,
    ) -> dict:
        """
        Iterate through the model YAML and update dictionary fields if needed.
        """

        updated = False
        try:
            for model_number, model in enumerate(model_yaml["models"]):
                if "columns" in model:
                    for col_num, model_column in enumerate(model["columns"]):
                        if self.dictionary_yml["dictionary"] is not None:
                            for dict_num, dict_column in enumerate(
                                self.dictionary_yml["dictionary"]
                            ):
                                if (
                                    model_column["name"] == dict_column["name"]
                                    or model_column["name"]
                                    in dict_column["aliases"]
                                ):
                                    if (
                                        "description"
                                        in model_yaml["models"][model_number][
                                            "columns"
                                        ][col_num]
                                    ):
                                        if (
                                            model_yaml["models"][model_number][
                                                "columns"
                                            ][col_num]["description"]
                                            != dict_column["description"]
                                            and dict_column["description"] != ""
                                        ):
                                            model_yaml["models"][model_number][
                                                "columns"
                                            ][col_num][
                                                "description"
                                            ] = dict_column["description"]
                                            logging.info(
                                                f"Field '{model_column['name']}' in file '{file_path}' has been updated."
                                            )
                                            updated = True
                                    elif dict_column["description"] != "":
                                        model_yaml["models"][model_number][
                                            "columns"
                                        ][col_num] = utils.insert_dict_item(
                                            model_yaml["models"][model_number][
                                                "columns"
                                            ][col_num],
                                            "description",
                                            dict_column["description"],
                                            1,
                                        )
                                        logging.info(
                                            f"Field '{model_column['name']}' in file '{file_path}' has been updated."
                                        )
                                        updated = True
                                    if "models" in dict_column:
                                        if (
                                            model["name"]
                                            not in self.dictionary_yml[
                                                "dictionary"
                                            ][dict_num]["models"]
                                        ):
                                            self.dictionary_yml["dictionary"][
                                                dict_num
                                            ]["models"].append(model["name"])
                                    else:
                                        self.dictionary_yml["dictionary"][
                                            dict_num
                                        ]["models"] = [model["name"]]
                        _update_existing_field(
                            self.existing_fields, model_column, model, file_path
                        )
                else:
                    logging.warning(
                        f"No columns found for model {model['name']} in '{file_path}'"
                    )
            if updated:
                return {"updated": True, "model_yaml": model_yaml}
        except Exception as error:
            logging.error(
                f"Error getting file updates for '{file_path}': {error}"
            )
        return {"updated": False}

    def collate_output_dictionary(self):
        """
        Collate metadata and update the data dictionary before writing to the
        dictionary file.
        """

        existing_field_descriptions = _collate_metadata(self.existing_fields)
        self.dictionary_yml["dictionary"] = existing_field_descriptions
        try:
            with open(self.dictionary_path, "w") as file:
                utils.YAML.dump(self.dictionary_yml, file)
                utils.add_spaces_between_cols(self.dictionary_path)
            logging.info(
                f"Dictionary '{self.dictionary_path}' has been updated"
            )
        except Exception as error:
            logging.error(
                f"There was a problem updating dictionary at '{self.dictionary_path}'. {error}"
            )
