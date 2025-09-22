import logging
import subprocess

import ruamel.yaml


def parse_bash_outputs(input_string) -> str:
    """
    This function parses the bash output represented by `input_string`, extracts and returns the portion of the
    output starting from the occurrence of the substring 'version: 2' to the end.

    If 'version: 2' is not found, it returns an empty string. In case of any exceptions during the execution,
    it logs an error message with details of the exception.

    Args:
        input_string (str): The bash output as a string.

    Returns:
        str: The substring of `input_string` starting from 'version: 2' to the end. If 'version: 2' is not found,
             it returns an empty string.
    """
    try:
        version_two_index = input_string.find("version: 2")
        if version_two_index != -1:
            return input_string[version_two_index:]
        return ""
    except Exception as e:
        logging.error("There was an issue parsing the codegen outputs: " + e)


def validate_dbt() -> bool:
    """
    Validates the dbt project to ensure its integrity and required dependencies.

    This function performs the following checks to validate the dbt project:
    1. Runs `dbt debug` to check if the project passes all the debug checks. If there are any issues, it logs the
       encountered errors and returns False.
    2. Checks if `dbt-labs/codegen` is installed as a dependency using `dbt deps` command. If the required package is
       not found, it logs an error message and returns False.
    3. If both the above checks pass successfully, it logs a success message confirming the successful validation
       of the dbt project and returns True.

    Returns:
        bool: True if the dbt project is successfully validated; False otherwise.
    """
    logging.info("Validating dbt project...")
    try:
        # Check debug passes
        bash_command = ["dbt", "debug"]
        result = subprocess.run(  # noqa: S603
            bash_command,
            check=False,
            capture_output=True,
        ).stdout.decode("UTF-8")
        if "All checks passed!" not in result:
            logging.error(
                "Issues encountered when running `dbt debug`. Validate `dbt debug` passes before retrying."
            )
            return False

        # Check codegen installed
        bash_command = ["dbt", "deps"]
        result = subprocess.run(  # noqa: S603
            bash_command,
            check=False,
            capture_output=True,
        ).stdout.decode("UTF-8")
        if "dbt-labs/codegen" not in result:
            logging.error(
                "dbt-labs/codegen is required to perform this operation"
            )
            return False

        # Otherwise confirm valid
        logging.info("dbt project successfully validated")
        return True

    except Exception as e:
        logging.error(
            "Issues encountered when attempting to validate dbt: " + e
        )
        return False


def get_model_yaml(model_names) -> str:
    """
    Generates the base model YAML for the specified model names.

    This function generates the base model YAML for the provided model names using dbt codegen's `generate_model_yaml`
    operation. The function performs the following steps:
    1. Logs an information message indicating the start of generating the base model YAML for the given model names.
    2. Constructs the arguments for the `dbt run-operation generate_model_yaml` command with the specified model names.
    3. Executes the command using `subprocess.run()` and captures the command's standard output as a string.
    4. Checks if there are any compilation errors in the output. If found, it logs an error message with the
       encountered issues and does not proceed further.
    5. If the output is error-free, it loads the output string into a YAML object using the `ruamel.yaml` library and
       returns the YAML content as a string.

    Parameters:
        model_names (list): A list of model names for which the base model YAML needs to be generated.

    Returns:
        str: The generated base model YAML as a string.

    Note:
        To use this function, the dbt CLI must be installed and accessible in the environment where this function is run.
    """
    try:
        logging.info(
            f"Generating base model for models: {', '.join(model_names)}"
        )
        args = {"model_names": model_names}
        bash_command = [
            "dbt",
            "run-operation",
            "generate_model_yaml",
            "--args",
            str(args),
        ]
        result = subprocess.run(  # noqa: S603
            bash_command,
            check=False,
            capture_output=True,
        ).stdout.decode("UTF-8")
        if "Compilation Error" in result:
            logging.error(
                "Issues encountered when generating the model yaml: " + result
            )
        else:
            yaml = ruamel.yaml.YAML()
            return yaml.load(parse_bash_outputs(result))
    except Exception as e:
        logging.error(f"Issues encountered when generating the model yaml: {e}")
