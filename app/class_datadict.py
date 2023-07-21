import ruamel.yaml
import logging
import os

class datadict:

    def __init__(self, dictionary_file_path, detailed_logs=True) -> None:
        """
        Initialize the object with the given dictionary file path and detailed logging settings.

        This constructor method is used to initialize an instance of the class. It sets the attributes
        'detailed_logs', 'dictionary_path', 'dictionary_yml', 'dictionary_items', 'existing_fields',
        and 'missing_fields' based on the provided inputs. The method also initializes logging and YAML
        configurations and loads the dictionary from the specified file.

        Parameters:
            dictionary_file_path (str): The file path to the YAML dictionary file.
            detailed_logs (bool, optional): Determines whether detailed log messages with 'info' level
                                            should be logged. Defaults to True.

        Returns:
            None
        """
        self.detailed_logs = detailed_logs
        self._init_logging()
        self._init_yaml()
        self.dictionary_path = dictionary_file_path
        self.dictionary_yml = self._load_dictionary()
        self._format_dictionary()
        self.dictionary_items = self._parse_aliases(self.dictionary_yml)
        self.existing_fields = []
        self.missing_fields = []

    def _init_yaml(self) -> None:
        """
        Initialize the YAML object and apply YAML configuration.

        This private method is used to initialize the YAML serializer object from the 'ruamel.yaml' library
        and apply specific configuration settings to it using the '_apply_yaml_config()' method.

        Parameters:
            None

        Returns:
            None
        """
        self.yaml = ruamel.yaml.YAML()
        self._apply_yaml_config()
    
    def _apply_yaml_config(self) -> None:
        """
        Apply YAML configuration settings.

        This private method is used to apply specific configuration settings to the YAML serializer in the
        object. It sets 'preserve_quotes' to True, which preserves quotes around strings in the output YAML.
        Additionally, it configures the indentation for mappings and sequences and sets the 'width' parameter
        for line wrapping in the output YAML.

        Parameters:
            None

        Returns:
            None
        """
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.width = 200
    
    def _init_logging(self):
        """
        Initialize logging configuration for the object.

        This private method is used to set up the logging configuration for the object. It configures the
        logging level to INFO and specifies the format of the log messages to display the log level and the
        log message text.

        Parameters:
            None

        Returns:
            None
        """
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    def _log(self, message, level='info') -> None:
        """
        Logs a message with the specified log level.

        This private method is used for logging messages with different log levels, such as 'info', 'warning',
        and 'error'. If 'detailed_logs' is set to True, messages with 'info' log level will also be logged.

        Parameters:
            message (str): The log message to be recorded.
            level (str, optional): The log level to use. Accepted values are 'info' (default), 'warning', and 'error'.

        Returns:
            None
        """
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
            self._log(f"An error occurred while creating the file '{self.dictionary_path}'. Check the directory exists.", level='error')
            raise SystemExit
    
    def _format_dictionary(self) -> None:
        """
        Format the dictionary data to ensure consistent structure.

        This private method is used to format the YAML dictionary data to ensure that each field in the
        'dictionary' key contains 'description' and 'aliases' keys. If any field is missing the 'description'
        or 'aliases' keys, they will be added with appropriate default values. If the 'dictionary' key does
        not exist in the YAML data, it will be created with an empty list as the value.

        Parameters:
            None

        Returns:
            None
        """
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

    def _parse_aliases(self, dictionary) -> list:
        """
        Parse dictionary data to extract field names and their aliases.

        This private method is used to parse the YAML dictionary data and extract field names along with their
        associated aliases. The function searches for the 'dictionary' key in the provided 'dictionary' parameter,
        and if it exists, it iterates through each field to gather the field name and its aliases, if available.

        Parameters:
            dictionary (dict): The YAML dictionary data to be parsed.

        Returns:
            list: A list containing the field names and their aliases (if available).
        """
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
    

    def _open_model_yml_file(self, file_path) -> dict:
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
            yaml = self.yaml.load(file)
            if self._check_valid_model_file(yaml):
                return {"status": "valid", "yaml": yaml}
            else:
                self._log(f"File '{file_path}' was skipped")
                return {"status": "invalid", "yaml": yaml}


    def _check_valid_model_file(self, yaml) -> bool:
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
            valid = yaml['models']
            return True
        except:
            return False

    def _insert_dict_item(self, dictionary, key, value, index) -> dict:
        """
        Insert a new key-value pair into a dictionary at the specified index.

        This private method is used to insert a new key-value pair into the provided dictionary at the given index.
        The function first extracts the keys and values from the dictionary, then inserts the new key and value at
        the specified index. Finally, it creates a new dictionary with the modified key-value pairs and returns it.

        Parameters:
            dictionary (dict): The dictionary to which the new key-value pair should be inserted.
            key (hashable): The key to insert into the dictionary.
            value (any): The value associated with the new key to be inserted.
            index (int): The index at which the new key-value pair should be inserted.

        Returns:
            dict: A new dictionary with the inserted key-value pair at the specified index.
        """
        keys = list(dictionary.keys())
        values = list(dictionary.values())
        keys.insert(index, key)
        values.insert(index, value)
        modified_dict = dict(zip(keys, values))
        return modified_dict
    
    def _update_existing_field(self, model_column, model, file_path) -> None:
        """
        Update the list of existing fields with model column details.

        This private method is used to update the list of existing fields by appending information about a model
        column found in a model YAML file. The function takes the 'model_column', 'model', and 'file_path' as inputs.
        If the 'model_column' contains a 'description' key, it appends a dictionary with the column name, description,
        model name, and file path to the 'existing_fields' list. If the 'description' key is not present, it appends a
        dictionary without the 'description' key.

        Parameters:
            model_column (dict): The model column dictionary from the model YAML.
            model (dict): The model dictionary representing the current model from the YAML file.
            file_path (str): The file path of the YAML file containing the model.

        Returns:
            None
        """
        if 'description' in model_column:
            self.existing_fields.append({"name": model_column['name'], "description": model_column['description'], "model":model['name'], "file": file_path})
        else:
            self.existing_fields.append({"name": model_column['name'], "model":model['name'], "file": file_path})

    def _iterate_dictionary_update(self, model_yaml, file_path) -> dict:
        """
        Iterate through the model YAML and update dictionary fields if needed.

        This private method iterates through the model YAML and updates dictionary fields if they are found
        in the 'dictionary_yml'. For each model in the 'model_yaml', it checks if the model column name matches
        any entry in the 'dictionary_yml' or its aliases. If a match is found and the model YAML contains a
        'description' for that field, it updates the description from the 'dictionary_yml'. If the 'description'
        is missing, it inserts the 'description' key with the appropriate value.

        Parameters:
            model_yaml (dict): The model YAML dictionary to be updated.
            file_path (str): The file path of the YAML file containing the model.

        Returns:
            dict: A dictionary with keys "updated" and "model_yaml". "updated" will be True if any updates were made,
                False otherwise. "model_yaml" will contain the updated model YAML data.
        """
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

    def _output_model_file(self, file_path, model_yaml) -> None:
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
            self.yaml.dump(model_yaml, file)
        self._log(f'File {file_path} has been updated')
    
    def _output_dictionary(self) -> None:
        """
        Output the updated dictionary YAML data to a file.

        This private method is used to write the updated dictionary YAML data to a file specified by 'dictionary_path'.
        The function takes the 'dictionary_yml' data from the class instance and writes it to the file using the YAML
        serializer.

        Parameters:
            None

        Returns:
            None
        """
        try:
            with open(self.dictionary_path, 'w') as file:
                self.yaml.dump(self.dictionary_yml, file)
            self._log(f"Dictionary '{self.dictionary_path}' has been updated")
        except Exception as error:
            self._log(f"There was a problem updating dictionary '{self.dictionary_path}'. {error}", level='error')
    
    def _get_missing_fields(self, existing_fields) -> list:
        """
        Get a list of missing fields not present in the dictionary.

        This private method is used to compare the 'existing_fields' with the 'dictionary_items' and find the
        fields that are present in 'existing_fields' but not in the dictionary. It returns a list of missing
        fields.

        Parameters:
            existing_fields (list): A list of dictionaries containing information about existing fields.

        Returns:
            list: A list of dictionaries representing the missing fields.
        """
        expected_field_names = set(field['name'] for field in existing_fields)
        existing_field_names = set(self.dictionary_items)
        missing_fields = expected_field_names - existing_field_names
        return [field for field in existing_fields if field['name'] in missing_fields]


    def apply_data_dictionary_to_file(self, file_path) -> None:
        """
        Apply the data dictionary updates to the specified model YAML file.

        This method applies the data dictionary updates to the specified 'file_path' representing a model YAML file.
        It checks if the file contains valid model data by using '_open_model_yml_file' function. If the file is
        valid, it iterates through the model YAML data and updates the descriptions of fields based on the entries
        in the 'dictionary_yml'. If any updates are made, it writes the updated YAML data back to the file using the
        '_output_model_file' function. If no updates are made, it logs a message stating that no updates were found.

        Parameters:
            file_path (str): The path to the model YAML file to which the data dictionary updates should be applied.

        Returns:
            None
        """
        self._log(f"Checking file '{file_path}'...")  
        model_yaml = self._open_model_yml_file(file_path)
        if model_yaml['status'] == 'valid':
            try:
                updates = self._iterate_dictionary_update(model_yaml['yaml'], file_path)
                if updates['updated']:
                    self._output_model_file(file_path, updates['model_yaml'])
                else:
                    self._log(f"No updates found for file '{file_path}'")
            
            except FileNotFoundError:
                self._log(f"File '{file_path}' not found.", level='error')
            except:
                self._log(f"Error processing file '{file_path}'", level='error')
        else:
            self._log(f"File '{file_path}' contains no models and has been skipped.")

    def apply_data_dictionary_to_path(self, directory) -> None:
        """
        Apply the data dictionary updates to all model YAML files in the specified directory and its subdirectories.

        This method applies the data dictionary updates to all model YAML files present in the specified 'directory'
        and its subdirectories. It iterates through the directory using os.walk and processes each YAML file using the
        'apply_data_dictionary_to_file' function.

        Parameters:
            directory (str): The path to the directory where model YAML files are located.

        Returns:
            None
        """
        if os.path.exists(directory) and os.path.isdir(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.yaml') or file.endswith('.yml'):
                        file_path = os.path.join(root, file)
                        self.apply_data_dictionary_to_file(file_path)
        else:
          self._log(f"Directory '{directory}' doesn't exist or can't be found", level='error')  
    
    def load_missing_fields(self):
        """
        Load missing fields into the data dictionary and update the dictionary YAML.

        This method loads missing fields into the data dictionary based on the 'existing_fields' information.
        It first collates metadata from the 'existing_fields' list using '_collate_metadata' method. It then
        identifies the missing fields by comparing the collated metadata with the 'dictionary_items' and retrieves
        the missing fields using the '_get_missing_fields' method. If any missing fields are found, they are added
        to the 'dictionary_yml' under the key 'missing_fields'. If no missing fields are found and 'missing_fields'
        key already exists in 'dictionary_yml', it is removed. Finally, the updated 'dictionary_yml' is output to
        the dictionary file using the '_output_dictionary' method.

        Parameters:
            None

        Returns:
            None
        """
        existing_field_descriptions = self._collate_metadata(self.existing_fields)
        missing_fields = self._get_missing_fields(existing_field_descriptions)
        if len(missing_fields) > 0:
            self.dictionary_yml['missing_fields'] = missing_fields
        elif 'missing_fields' in self.dictionary_yml:
            del(self.dictionary_yml['missing_fields'])
        self._output_dictionary()
