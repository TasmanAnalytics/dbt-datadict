import datadict
import click

@click.group()
def cli():
    pass

@cli.command()
@click.option('-d', '--dictionary', type=str, help='Location of the dictionary file', default='datadictionary.yml')
@click.option('-D', '--directory', type=str, help='Directory to apply dictionary', default='models/')
def apply(dictionary, directory):
    dictionary = datadict.datadict(dictionary, detailed_logs=True)
    dictionary.apply_data_dictionary_to_path(directory)
    dictionary.collate_output_dictionary()

@cli.command()
@click.option('-D', '--directory', type=str, help='Directory to apply dictionary', default='models/')
@click.option('-n', '--name', type=str, help='Name to give the generated YAML file', default='models.yml')
def generate(directory, name):
    datadict.generate_model_yamls(directory, name)