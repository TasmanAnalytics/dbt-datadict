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
    with open(file, 'r') as f:
            yaml = str(f.read())
    replaced = yaml.replace('  - name:', '\n  - name:')
    with open(file, 'w') as f:
        f.write(replaced)

def open_model_yml_file(yaml_obj, file_path) -> dict:
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
    with open(file_path, 'r+') as file:
        yaml = yaml_obj.load(file)
        if check_valid_model_file(yaml):
            return {"status": "valid", "yaml": yaml}
        else:
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
        valid = model_yaml['models']
        return True
    except:
        return False
    
def output_model_file(yaml_obj, file_path, model_yaml) -> None:
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
    with open(file_path, 'w') as file:
        yaml_obj.dump(model_yaml, file)
