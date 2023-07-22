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