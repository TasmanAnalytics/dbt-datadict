import json
import logging
import os
import subprocess
from datetime import datetime, timedelta

import ijson
import ruamel.yaml


def parse_bash_outputs(input_string: str) -> str | None:
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
    2. Checks if `dbt-labs/codegen` is installed as a dependency using `dbt deps` command. If not found, logs a
       warning (codegen is now optional; manifest-based extraction is used if available).
    3. If debug passes, it logs a success message confirming validation and returns True.

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

        # Check codegen installed (warning only, now optional)
        bash_command = ["dbt", "deps"]
        result = subprocess.run(  # noqa: S603
            bash_command,
            check=False,
            capture_output=True,
        ).stdout.decode("UTF-8")
        if "dbt-labs/codegen" not in result:
            logging.warning(
                "dbt-labs/codegen not found - will use manifest for column metadata if available"
            )

        # Otherwise confirm valid
        logging.info("dbt project successfully validated")
        return True

    except Exception as e:
        logging.error(
            "Issues encountered when attempting to validate dbt: " + e
        )
        return False


def get_manifest_path() -> str | None:
    """
    Find target/manifest.json, validating we're in a dbt project.

    Returns:
        str: Absolute path to manifest.json, or None if not found or not in dbt project.
    """
    if not os.path.exists("dbt_project.yml"):
        logging.error(
            "Not in a dbt project directory (dbt_project.yml not found). "
            "Please run from your dbt project root."
        )
        return None

    manifest_path = "target/manifest.json"
    if os.path.exists(manifest_path):
        return os.path.abspath(manifest_path)

    return None


def is_manifest_fresh(manifest_path: str, max_age_hours: int = 24) -> bool:
    """
    Check if manifest was generated recently using metadata.generated_at.

    Uses streaming to read only the metadata section, avoiding loading entire file.

    Args:
        manifest_path: Path to manifest.json
        max_age_hours: Maximum age before considering stale (default: 24 hours)

    Returns:
        bool: True if manifest is fresh, False if stale or invalid
    """
    try:
        with open(manifest_path, "rb") as f:
            parser = ijson.items(f, "metadata")
            for metadata in parser:
                generated_at_str = metadata.get("generated_at")
                if not generated_at_str:
                    logging.warning(
                        "Manifest missing generated_at timestamp"
                    )
                    return False

                generated_at = datetime.fromisoformat(
                    generated_at_str.replace("Z", "+00:00")
                )
                age = datetime.now(generated_at.tzinfo) - generated_at
                is_fresh = age < timedelta(hours=max_age_hours)

                if not is_fresh:
                    logging.warning(
                        f"Manifest is {age.total_seconds() / 3600:.1f} hours old "
                        f"(threshold: {max_age_hours} hours)"
                    )

                return is_fresh

        logging.warning("Manifest missing metadata section")
        return False

    except Exception as e:
        logging.error(f"Failed to check manifest freshness: {e}")
        return False


def generate_manifest() -> bool:
    """
    Generate or refresh the manifest.json by running dbt parse.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logging.info("Generating manifest via 'dbt parse'...")
        bash_command = ["dbt", "parse"]
        result = subprocess.run(  # noqa: S603
            bash_command,
            check=False,
            capture_output=True,
        )

        if result.returncode != 0:
            logging.error(f"dbt parse failed: {result.stderr.decode('UTF-8')}")
            return False

        if not os.path.exists("target/manifest.json"):
            logging.error("Manifest.json not created after dbt parse")
            return False

        logging.info("Manifest generated successfully")
        return True

    except Exception as e:
        logging.error(f"Failed to generate manifest: {e}")
        return False


def extract_columns_from_manifest_streaming(
    manifest_path: str, model_names: list[str]
) -> dict | None:
    """
    Extract column metadata using streaming JSON parsing for large manifests.

    CRITICAL: Manifests can be 1.6GB+. Never load entire file into memory.
    Uses ijson library to parse incrementally.

    Args:
        manifest_path: Path to manifest.json
        model_names: List of model names to extract

    Returns:
        dict: Column metadata in standard format {"version": 2, "models": [...]},
              or None if extraction fails
    """
    model_names_set = set(model_names)
    models_list = []

    try:
        with open(manifest_path, "rb") as f:
            parser = ijson.kvitems(f, "nodes")

            for node_key, node_data in parser:
                if node_data.get("resource_type") != "model":
                    continue
                if node_data.get("name") not in model_names_set:
                    continue

                columns_dict = node_data.get("columns", {})
                columns_list = [
                    {
                        "name": col_data.get("name", col_name),
                        "data_type": col_data.get("data_type", ""),
                        "description": col_data.get("description", ""),
                    }
                    for col_name, col_data in columns_dict.items()
                ]
                columns_list.sort(key=lambda x: x["name"])

                models_list.append(
                    {
                        "name": node_data.get("name"),
                        "columns": columns_list,
                    }
                )

                if len(models_list) == len(model_names_set):
                    break

        if not models_list:
            logging.warning(
                f"No models found in manifest: {model_names}"
            )
            return None

        return {"version": 2, "models": models_list}

    except Exception as e:
        logging.error(f"Failed to stream-parse manifest: {e}")
        return None


def get_columns_from_manifest(model_names: list[str]) -> dict | None:
    """
    Orchestrate manifest-based extraction with auto-generation.

    Attempts to extract column metadata from manifest, automatically generating
    it if missing or stale.

    Args:
        model_names: List of model names to extract

    Returns:
        dict: Column metadata in standard format, or None if extraction fails
    """
    # 1. Locate manifest
    manifest_path = get_manifest_path()
    if not manifest_path:
        logging.info("Manifest not found, attempting to generate...")
        if not generate_manifest():
            logging.warning("Failed to generate manifest")
            return None
        manifest_path = get_manifest_path()
        if not manifest_path:
            return None

    # 2. Check freshness
    if not is_manifest_fresh(manifest_path):
        logging.info("Manifest is stale, regenerating...")
        if not generate_manifest():
            logging.warning(
                "Failed to regenerate manifest, using stale version"
            )

    # 3. Read and extract
    return extract_columns_from_manifest_streaming(manifest_path, model_names)


def _get_model_yaml_from_database(model_names: list[str]) -> dict | None:
    """
    Generate base model YAML using dbt-codegen (database query).

    Original implementation using dbt run-operation generate_model_yaml.

    Args:
        model_names: List of model names to generate YAML for

    Returns:
        dict: The generated base model YAML as a dict
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

    return None


def get_model_yaml(model_names: list[str]) -> dict | None:
    """
    Generates the base model YAML for the specified model names.

    Attempts to extract column metadata from manifest first (recommended). Falls
    back to database query via dbt-codegen if manifest approach fails.

    Parameters:
        model_names: A list of model names for which to generate base YAML

    Returns:
        dict: The generated base model YAML as a dict, or None on failure
    """
    # 1. Try manifest-first approach
    logging.info("Attempting to extract column metadata from manifest...")
    manifest_result = get_columns_from_manifest(model_names)

    if manifest_result:
        models_found = {m["name"] for m in manifest_result["models"]}
        models_missing = set(model_names) - models_found

        if models_missing:
            logging.info(
                f"Models not found in manifest: {models_missing}. "
                "Falling back to database for these models."
            )
            db_result = _get_model_yaml_from_database(list(models_missing))
            if db_result:
                manifest_result["models"].extend(db_result["models"])

        return manifest_result

    # 2. Fallback to database approach
    logging.info(
        "Manifest approach failed. Falling back to database query via dbt-codegen..."
    )
    return _get_model_yaml_from_database(model_names)
