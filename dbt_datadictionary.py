import app
import click

@click.group()
def cli():
    pass

@cli.command()
@click.option('-d', '--dictionary', type=str, help='Location of the dictionary file', default='datadictionary.yml')
@click.option('-D', '--directory', type=str, help='Directory to apply dictionary', default='models/')
def apply(dictionary, directory):
    dictionary = app.datadict(dictionary, detailed_logs=True)
    dictionary.apply_data_dictionary_to_path(directory)
    dictionary.load_missing_fields()
