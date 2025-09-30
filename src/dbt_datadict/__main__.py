import logging

import click

from dbt_datadict import apply as apply_
from dbt_datadict import generate as generate_

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)


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
    dictionary = apply_.DataDict(dictionary)
    apply_.apply_data_dictionary_to_path(
        directory,
        dictionary.iterate_dictionary_update,
    )
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
    "--unique-model-yaml",
    "unique_model_yaml",
    help="Creates one YAML for each model with the same name as the model",
    default=False,
)
@click.option(
    "--sort/--no-sort",
    help="Triggers the generated YAML files to be sorted alphabetically",
    default=True,
)
def generate(directory, file, unique_model_yaml, sort):
    """
    This command generates model YAML files in a specified directory. Existing model YAML files are evaluated,
    and the model metadata is combined and written back to the existing files. For models missing from existing files,
    a new file is created in the directory with the given name and the metadata for the missing models is written to it.
    """
    generate_.generate_model_yamls(directory, file, unique_model_yaml, sort)
