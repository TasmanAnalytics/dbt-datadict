def add_spaces_between_cols(file):
    with open(file, 'r') as f:
            yaml = str(f.read())
    replaced = yaml.replace('  - name:', '\n  - name:')
    with open(file, 'w') as f:
        f.write(replaced)