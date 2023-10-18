import click

import datadict


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "-d",
    "--dictionary",
    type=str,
    help="Location of the dictionary file",
    default="datadictionary.yml",
)
@click.option(
    "-D",
    "--directory",
    type=str,
    help="Directory to apply dictionary",
    default="models/",
)
def apply(dictionary, directory):
    """
    This command reviews all existing model files in the given directory for existing columns and collates them into a
    dictionary file. Additionally, this command will review the dictionary file and apply updates back to the columns in
    the model files where possible.
    """
    dictionary = datadict.datadict(dictionary, detailed_logs=True)
    dictionary.apply_data_dictionary_to_path(directory)
    dictionary.collate_output_dictionary()


@cli.command()
@click.option(
    "-D",
    "--directory",
    type=str,
    help="Directory to apply dictionary",
    default="models/",
)
@click.option(
    "-f",
    "--file",
    type=str,
    help="Name to give the generated YAML file",
    default="models.yml",
)
@click.option(
    "--sort/--no-sort",
    help="Triggers the generated YAML files to be sorted alphabetically",
    default=True,
)
def generate(directory, file, sort):
    """
    This command generates model YAML files in a specified directory. Existing model YAML files are evaluated,
    and the model metadata is combined and written back to the existing files. For models missing from existing files,
    a new file is created in the directory with the given name and the metadata for the missing models is written to it.
    """
    datadict.generate_model_yamls(directory, file, sort)
