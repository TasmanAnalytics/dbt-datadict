import subprocess
import os
import ruamel.yaml

def parse_bash_outputs(input_string) -> str:
    version_two_index = input_string.find('version: 2')
    if version_two_index != -1:
        return input_string[version_two_index:]
    else:
        return ''

def get_model_yaml(model_names) -> str:
    yaml = ruamel.yaml.YAML()
    print(f'Generating base model for models {model_names}')
    args = {"model_names": model_names}
    bash_command = ["dbt", "run-operation", "generate_model_yaml", "--args", str(args)]
    result = subprocess.run(bash_command, capture_output=True).stdout.decode('UTF-8')
    return yaml.load(parse_bash_outputs(result))

def list_directory_yml_files(directory) -> dict:
    files_list = []
    if os.path.exists(directory) and os.path.isdir(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.yaml') or file.endswith('.yml'):
                        files_list.append(os.path.join(root, file))
    return files_list

def open_yaml_file(file_path) -> dict:
    yaml = ruamel.yaml.YAML()
    with open(file_path, 'r+') as file:
            yaml_file = yaml.load(file)
    if 'models' in yaml_file:
        return yaml_file

def check_files_for_models(files) -> dict:
    model_list = []
    for file_path in files:
        yaml = open_yaml_file(file_path)
        if yaml is not None:
            for model in yaml['models']:
                model_list.append({'name': model['name'], 'file': file_path})
    return model_list

def combine_column_lists(current_yml, expected_yml) -> dict:
    combined_dict = current_yml.copy()
    # Iterate through the columns of dict2 and add the missing ones to combined_dict
    for column in expected_yml.get('columns', []):
        name = column.get('name')
        if name is not None:
            # Check if the name is already present in combined_dict
            found = False
            for existing_column in combined_dict.get('columns', []):
                if existing_column.get('name') == name:
                    found = True
                    break

            # If the name is not already present, add the column to combined_dict
            if not found:
                combined_dict.setdefault('columns', []).append(column)

    return combined_dict

def main():
    model_list = []
    files = list_directory_yml_files('models/')
    models = check_files_for_models(files)
    for model in models:
        model_list.append(model['name'])
    model_yaml = get_model_yaml(model_list)
    print(model_yaml)
            
                         
main()