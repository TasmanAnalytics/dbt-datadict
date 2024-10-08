import logging
import os

import ruamel.yaml

from datadict import datadict_dbt, datadict_helpers


def check_files_for_models(yaml_obj, files) -> dict:
    try:
        file_yamls = []
        model_list = []
        for file_path in files:
            file_contents = datadict_helpers.open_model_yml_file(yaml_obj, file_path)
            if file_contents["status"] == "valid":
                try:
                    for model in file_contents["yaml"]["models"]:
                        model_list.append({"name": model["name"], "file": file_path})
                    file_yamls.append(
                        {"file_path": file_path, "file_yaml": file_contents["yaml"]}
                    )
                except Exception as error:
                    logging.error(
                        f"There was an issue processing file '{file_path}'. Ensure it is formatted correctly and retry. Error: {error}"
                    )
        return {"model_list": model_list, "file_yamls": file_yamls}
    except Exception as error:
        logging.error(
            f"Issues encountered when iterating through files to collect models. Error: {error}"
        )


def combine_column_lists(current_yml, expected_yml) -> dict:
    updated = False
    combined_yaml = current_yml.copy()
    existing_columns = combined_yaml.setdefault("columns", [])
    # Iterate through the columns of expected_yml and add the missing ones to current_yml
    for column in expected_yml.get("columns", []):
        name = column.get("name")
        if name is not None:
            # Check if the name is already present in current_yml
            found = False
            for existing_column in combined_yaml.get("columns", []):
                if existing_column.get("name") == name:
                    found = True
                    break

            # If the name is not already present, add the column to current_yml
            if not found:
                combined_yaml.setdefault("columns", []).append(column)
                updated = True
                logging.warning(
                    f"Missing column '{column['name']}' to be added to model '{current_yml['name']}'"
                )
       
	# Iterate through the existing columns and remove any that are not in the expected_yml
    columns_to_remove = []
    for existing_column in existing_columns:
        name = existing_column.get("name")
        if name is not None:
            found = False
            for column in expected_yml.get("columns", []):
                if column.get("name") == name:
                    found = True
                    break
            if not found:
                columns_to_remove.append(existing_column)

    if columns_to_remove:
        for column in columns_to_remove:
            existing_columns.remove(column)
            updated = True
            logging.warning(
                f"Column '{column['name']}' removed from model '{current_yml['name']}'"
            )
    
	# Add the data_type to any columns that are missing it & set empty description if missing
    data_types_dict = {column['name']: column['data_type'] for column in expected_yml.get("columns", [])}

    for column in combined_yaml['columns']:
        if 'data_type' not in column:
            column['data_type'] = data_types_dict[column['name']]
            updated = True
            logging.info(
			    f"Added data_type '{column['data_type']}' to '{column['name']}' in model '{current_yml['name']}'"
		    )

    sort_order = ['name', 'data_type', 'description', 'tests', 'data_tests', 'unit_tests', 'meta']
    
    for column in combined_yaml['columns']:
        column['description'] = column.get('description', '')

        for optional_columns in ['tests', 'data_tests', 'unit_tests', 'meta']:
            if optional_columns in column:
                column[optional_columns] = column[optional_columns]
            else:
                column.pop(optional_columns, None)

        column_sorted = {key: column[key] for key in sort_order if key in column}
        
        column.clear()
        column.update(column_sorted)
    
    return {"yaml": combined_yaml, "updated": updated}


def updated_existing_files(yaml_obj, existing_file_yamls, models_to_be_updated, sort):
    # loop through each existing file
    updated_count = 0
    for file in existing_file_yamls:
        file_yaml = file["file_yaml"]
        path = file["file_path"]

        try:
            for model_num, model in enumerate(file_yaml["models"]):
                    for model_to_be_updated in models_to_be_updated:
                        if model_to_be_updated["name"] == model["name"]:
                            logging.info(f"Model {model['name']} is being checked...")
                            combined_columns = combine_column_lists(
                                model, model_to_be_updated
                            )
                            file_yaml["models"][model_num] = combined_columns["yaml"]
                            updated = combined_columns["updated"]
                            if updated:
                                updated_count += 1
                            else:
                                logging.info(f"Model {model['name']} is correct")

            if updated_count > 0:
                    datadict_helpers.output_model_file(yaml_obj, path, file_yaml, sort)
        except Exception as error:
            logging.error(
                f"There was an issue processing file '{path}'. This is likely a badly formatted YAML file. Error: {error}"
            )


def add_missing_models(yaml_obj, path, models, sort):
    if os.path.isfile(path) and os.path.exists(path):
        yaml = datadict_helpers.open_model_yml_file(yaml_obj, path)
        if yaml["status"] == "valid":
            logging.info(f"File '{path}' has been found and is a valid models file")
            updated = yaml["yaml"]
            if len(models) > 0:
                updated["models"] = updated["models"] + models
                datadict_helpers.output_model_file(yaml_obj, path, updated, sort)
            else:
                logging.info(f"No updates to apply to '{path}'")
        else:
            logging.error(
                f"File '{path}' has been found and but isn't a valid model file"
            )
    else:
        logging.info(f"File '{path}' doesn't exist and will be created.")
        file_yaml = {"version": 2, "models": models}
        datadict_helpers.output_model_file(yaml_obj, path, file_yaml, sort)
        
def yaml_for_each_model(yaml_obj, model_file_list, existing_file_yamls, existing_model_list, models_to_be_added):
    """
    Check for each model if the current YAML file matches the expected YAML file. The expected YAML 
    file has the same name as the model file, but with a .yml extension.

    Parameters:
        yaml_obj (object): The YAML object.
        model_file_list (list): List of model file paths.
        existing_file_yamls (list): List of dictionaries with existing file YAMLs.
        existing_model_list (list): List of dictionaries with with existing models.
        models_to_be_added (list): List of dictionaries with models to be added.

    Returns:
        None
    """

    model_dicts = [{
        'name': os.path.splitext(os.path.basename(file))[0],
        'model_path': file,
        'expected_yml_path': file.replace('.sql', '.yml')
    } for file in model_file_list]

    existing_models = []

    for item in existing_file_yamls:
        if "models" in item["file_yaml"]:
            existing_models.extend(item["file_yaml"]["models"])
    
    combined_dicts = []

    for item1 in model_dicts:
        name = item1["name"]
        item2 = next((item for item in models_to_be_added if item["name"] == name), {})
        item3 = next((item for item in existing_model_list if item["name"] == name), {})
        item4 = next((item for item in existing_models if item["name"] == name), {})
        
        combined_dict = {**item1, **item2, **item3, **item4}
        combined_dicts.append(combined_dict)

    for dict in combined_dicts:
        dict.setdefault('file', None)
    
    files_to_remove = set()

    for model in combined_dicts:
        if model['file'] != model['expected_yml_path']:

            model_to_write = model.copy()
            model_to_write.pop('file', None)
            model_to_write.pop('model_path', None)
            model_to_write.pop('expected_yml_path', None)
            model_to_write = {
                'version': 2,
                'models': [model_to_write]
            } 

            datadict_helpers.output_model_file(yaml_obj, model['expected_yml_path'], model_to_write, sort=False)
            
            if model['file'] is not None:
                files_to_remove.add(model['file'])
                logging.info(f"Model '{model['name']}' is being split into its own yaml file.")

        else:
            logging.info(f"Model '{model['name']}' is correct")
            
    for file in files_to_remove:
        os.remove(file)


def generate_model_yamls(directory, name, unique_model_yaml, sort=True):
    """
    Generate model YAML files in a given directory.

    This function generates model YAML files in a specified directory. Existing model YAML files are evaluated,
    and the model metadata is combined and written back to the existing files. For models missing from existing files,
    a new file is created and the metadata for the missing models is written to it.

    Parameters:
        directory (str): The directory where the model YAML files are located, and where new files will be created.

        name (str): The base name of the new YAML file to be created for models missing from existing files.

        sort (bool, optional): Whether to sort the models alphabetically by their name. Default is False.

    Returns:
        None

    Raises:
        Exception: If any error occurs during the generation of the YAML files, an error message is logged and the
        exception is raised.

    Note:
        This function is part of a larger data dictionary process that requires a valid DBT (Data Build Tool)
        configuration and a set of SQL and YAML files containing DBT models and their metadata.
    """
    try:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        yaml_obj = ruamel.yaml.YAML()
        yaml_obj.preserve_quotes = True
        yaml_obj.indent(mapping=2, sequence=4, offset=2)
        yaml_obj.width = 200

        # 1. Validate dbt is configured and usable
        if not datadict_dbt.validate_dbt():
            return

        # 2. Evaluate the existing yaml files in the directory for model metadata
        yaml_file_list = datadict_helpers.list_directory_files(
            directory, [".yml", ".yaml"]
        )
        if len(yaml_file_list) == 0:
            SystemExit
        existing_files = check_files_for_models(yaml_obj, yaml_file_list)
        existing_model_list = existing_files["model_list"]
        existing_file_yamls = existing_files["file_yamls"]

        # 3. Get the full column list for every model in the directory
        model_file_list = datadict_helpers.list_directory_files(directory, [".sql"])
        model_names = [os.path.basename(file).split(".")[0] for file in model_file_list]
        model_column_list = datadict_dbt.get_model_yaml(model_names)

        # 4. Split out the models in existing files from models missing from existing files.
        models_to_be_updated = []
        models_to_be_added = []

        for model_num, model in enumerate(model_column_list["models"]):
            if any(
                existing_model["name"] == model["name"]
                for existing_model in existing_model_list
            ):
                models_to_be_updated.append(model_column_list["models"][model_num])
            else:
                models_to_be_added.append(model_column_list["models"][model_num])

        # 5. For models in existing files, combine the column lists and write back to the existing file 
        if len(models_to_be_updated) > 0:
            logging.info(f"There are {len(models_to_be_updated)} models to be checked")
            updated_existing_files(
                yaml_obj, existing_file_yamls, models_to_be_updated, sort
            )
        else:
            logging.info("There are no models requiring updating.")

        # 6. For models missing from existing files, create a new file with the given name and output the metadata
        if unique_model_yaml:
            yaml_for_each_model(yaml_obj, model_file_list, existing_file_yamls, existing_model_list, models_to_be_added)
        elif len(models_to_be_added) > 0:
            file_name = os.path.join(directory, name)
            logging.info(
                f"There are {len(models_to_be_added)} models to be added to file '{file_name}'"
            )
            add_missing_models(yaml_obj, file_name, models_to_be_added, sort)
        else:
            logging.info("There are no models to be added.")

    except Exception as error:
        logging.error(f"There was an error generating the YAML files. Error: {error}")
