import pathlib

import pytest
import ruamel.yaml


@pytest.fixture(scope="function")
def temp_dir(tmp_path_factory) -> pathlib.Path:
    """
    A temporary working directory.
    """

    return tmp_path_factory.mktemp("temp_dir")


@pytest.fixture(scope="function")
def yaml_obj() -> ruamel.yaml.YAML:
    """
    A YAML object for reading and writing YAML files.
    """

    return ruamel.yaml.YAML()
