import ruamel.yaml
import logging
import os

class datadict:

    def __init__(self, dictionary_file_path, detailed_logs=True):
        self.detailed_logs = detailed_logs
        self._init_logging()
        self._init_yaml()
        self.dictionary_path = dictionary_file_path
        self.dictionary_yml = self._load_dictionary()
        self._format_dictionary()
        self.dictionary_items = self._parse_aliases(self.dictionary_yml)
        self.existing_fields = []
        self.missing_fields = []

    def _init_yaml(self):
        self.yaml = ruamel.yaml.YAML()
        self._apply_yaml_config()
    
    def _apply_yaml_config(self):
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.width = 200
    
    def _init_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    def _log(self, message, level='info'):
        if level == 'warning':
            logging.warning(message)
        elif level == 'error':
            logging.error(message)
        elif self.detailed_logs:
            logging.info(message)
    
    def _try_load_dictionary(self) -> dict:
        """
        Tries to load a dictionary from a given path, and if it doesn't exist, creates a new dictionary.

        This private method is used to load a dictionary from a specified path. If the file exists at the
        given path, it loads the dictionary using the `_load_dictionary()` method. If the file doesn't
        exist, it creates a new dictionary using the `_create_dictionary()` method.

        Returns:
            dict: A dictionary loaded from the specified path if the file exists, otherwise, a newly created dictionary.
        """
        if os.path.exists(self.dictionary_path):
            return self._load_dictionary()
        else:
            return self._create_dictinary()

    def _load_dictionary(self) -> dict:
        """
        Loads a dictionary from a specified path.

        This private method is used to read and load a dictionary from a given YAML file path. It attempts
        to open the file, read its content, and parse it as a YAML formatted dictionary.

        Returns:
            dict: The dictionary loaded from the specified YAML file.

        Raises:
            FileNotFoundError: If the file at the specified path does not exist.
            Exception: If an error occurs while loading the dictionary from the YAML file.
        """
        try:
            with open(self.dictionary_path, 'r') as file:
                self._log(f"Dictionary file '{self.dictionary_path}' loaded successfully.")
                return self.yaml.load(file)
        except FileNotFoundError:
            self._log(f"Dictionary file '{self.dictionary_path}' not found.", level='error')
        except:
            self._log(f"Error loading dictionary file '{self.dictionary_path}'", level='error')
            

    def _create_dictinary(self) -> dict:
        """
        Creates a new dictionary and saves it to a specified path.

        This private method is used to create a new dictionary, serialize it as a YAML formatted data,
        and save it to a given file path. The created dictionary will have an initial structure of
        'base_yaml = {'dictionary': []}'.

        Returns:
            dict: The newly created dictionary.

        Raises:
            IOError: If an error occurs while creating or writing to the file.
            SystemExit: If a critical error occurs during the creation process.
        """
        try:
            with open(self.dictionary_path, 'w') as file:
                base_yaml = {'dictionary': []}
                self.yaml.dump(base_yaml, file)
                self._log(f"The file '{self.dictionary_path}' was successfully created.")
            with open(self.dictionary_path, 'r') as file:
                self._log(f"Dictionary file '{self.dictionary_path}' loaded successfully.")
                return self.yaml.load(file)
        except IOError:
            self._log(f"An error occurred while creating the file '{self.dictionary_path}'.", level='error')
            raise SystemExit
    
    def _format_dictionary(self):
        try:
            if 'dictionary' in self.dictionary_yml:
                if self.dictionary_yml['dictionary'] is not None:
                    for field_num, field in enumerate(self.dictionary_yml['dictionary']):
                        if 'description' not in field:
                            self.dictionary_yml['dictionary'][field_num]['description'] = ''
                        if 'aliases' not in field:
                            self.dictionary_yml['dictionary'][field_num]['aliases'] = []
            else:
                self.dictionary_yml['dictionary'] = []
        except TypeError:
            self._log('There was an error when trying to format the dictionary')

    def _parse_aliases(self, dictionary):
        try:
            values = []
            if dictionary['dictionary'] is None:
                return values
            for dict_column in dictionary['dictionary']:
                values.append(dict_column['name'])
                try:
                    for alias in dict_column['aliases']:
                        values.append(alias)
                except:
                    values.append('')
            return values
        except TypeError:
            self._log('There was an error when trying to parse the dictionary')
    

    def _open_yml_file(self, file_path):
        with open(file_path, 'r+') as file:
            yaml = self.yaml.load(file)
            if self._check_valid_model_file(yaml):
                return {"status": "valid", "yaml": yaml}
            else:
                self._log(f"File '{file_path}' was skipped")
                return {"status": "invalid", "yaml": yaml}


    def _check_valid_model_file(self, yaml):
        try:
            valid = yaml['models']
            return True
        except:
            return False

    def _insert_dict_item(self, dictionary, key, value, index):
        keys = list(dictionary.keys())
        values = list(dictionary.values())
        keys.insert(index, key)
        values.insert(index, value)
        modified_dict = dict(zip(keys, values))
        return modified_dict
    
    def _update_existing_field(self, model_column, model, file_path):
        if 'description' in model_column:
            self.existing_fields.append({"name": model_column['name'], "description": model_column['description'], "model":model['name'], "file": file_path})
        else:
            self.existing_fields.append({"name": model_column['name'], "model":model['name'], "file": file_path})

    def _iterate_dictionary_update(self, model_yaml, file_path):
        try:
            for model_number, model in enumerate(model_yaml['models']):
                for col_num, model_column in enumerate(model['columns']):
                    self._update_existing_field(model_column, model, file_path)
                    if self.dictionary_yml['dictionary'] is not None:
                        for dict_column in self.dictionary_yml['dictionary']:
                            if model_column['name'] == dict_column['name'] or model_column['name'] in dict_column['aliases']:
                                if 'description' in model_yaml['models'][model_number]['columns'][col_num]:
                                    if model_yaml['models'][model_number]['columns'][col_num]['description'] != dict_column['description']:
                                        model_yaml['models'][model_number]['columns'][col_num]['description'] = dict_column['description']
                                        self._log(f"Field '{model_column['name']}' in file '{file_path}' has been updated.")
                                        return {"updated": True, "model_yaml": model_yaml}
                                else:
                                    model_yaml['models'][model_number]['columns'][col_num] = self._insert_dict_item(model_yaml['models'][model_number]['columns'][col_num], 'description', dict_column['description'], 1)
                                    self._log(f"Field '{model_column['name']}' in file '{file_path}' has been updated.")    
                                    return {"updated": True, "model_yaml": model_yaml}
        except Exception as error:
            self._log(f"Error getting file updates for '{file_path}': {error}", level='error')
        return  {"updated": False}

    def _collate_metadata(self, existing_fields) -> list:
        """
        Collates metadata from existing field list.

        This function takes a list of dictionaries representing existing fields and organizes the metadata
        by grouping fields based on their names. For each unique field name, it collects unique models and
        non-empty descriptions associated with the field.

        Parameters:
            existing_fields (list of dict): A list of dictionaries, where each dictionary contains information
                                            about an existing field with keys 'name', 'model', and optionally 'description'.

        Returns:
            list: A list of dictionaries containing collated metadata for each field. Each dictionary contains
                keys 'name', 'description', 'versions', and 'models'.

        Example:
            existing_fields = [
                {'name': 'booking_id', 'model': 'core__bookings_joined', 'description': 'Booking ID Description'},
                {'name': 'user_id', 'model': 'core__users_joined'},
                ...
            ]
            result = _collate_metadata(existing_fields)
        """
        metadata = {}
        result = []

        #extract metadata from existing field list
        for field in existing_fields:
            name = field['name']
            model = field['model']
            description = field.get('description', '')

            if name not in metadata:
                metadata[name] = {'versions': [description], 'description': description, 'models':[model]}
            else:
                metadata[name]['versions'].append(description)
                metadata[name]['models'].append(model)

        #summarise metadata
        for name, info in metadata.items():
            versions = list(set([version for version in info['versions'] if version != '']))
            versions.sort()
            models = list(set(info['models']))
            models.sort()
            result.append({'name': name, 'description': info['description'], 'versions': versions, 'models': models})

        #return field list sorted by name
        return sorted(result, key=lambda d: d['name'])

    def _output_model_file(self, file_path, model_yaml):
        with open(file_path, 'w') as file:
            self.yaml.dump(model_yaml, file)
    
    def _output_dictionary(self):
        with open(self.dictionary_path, 'w') as file:
            self.yaml.dump(self.dictionary_yml, file)
    
    def _get_missing_fields(self, existing_fields):
        expected_field_names = set(field['name'] for field in existing_fields)
        existing_field_names = set(self.dictionary_items)
        missing_fields = expected_field_names - existing_field_names
        return [field for field in existing_fields if field['name'] in missing_fields]


    def apply_data_dictionary_to_file(self, file_path):
        self._log(f"Checking file '{file_path}'...")  
        model_yaml = self._open_yml_file(file_path)
        if model_yaml['status'] == 'valid':
            try:
                updates = self._iterate_dictionary_update(model_yaml['yaml'], file_path)
                if updates['updated']:
                    self._output_model_file(file_path, updates['model_yaml'])
                    self._log(f'File {file_path} has been completed')
                else:
                    self._log(f'File {file_path} was skipped')
            
            except FileNotFoundError:
                self._log(f"File '{file_path}' not found.", level='error')
            except:
                self._log(f"Error processing file '{file_path}'", level='error')

    def apply_data_dictionary_to_path(self, directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    file_path = os.path.join(root, file)
                    self.apply_data_dictionary_to_file(file_path)
    
    def load_missing_fields(self):
        existing_field_descriptions = self._collate_metadata(self.existing_fields)
        missing_fields = self._get_missing_fields(existing_field_descriptions)
        if len(missing_fields) > 0:
            self.dictionary_yml['missing_fields'] = missing_fields
        elif 'missing_fields' in self.dictionary_yml:
            del(self.dictionary_yml['missing_fields'])
        self._output_dictionary()
