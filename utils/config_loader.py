import json
import logging


def load_json_file(json_file: str):
    """
    Loads a JSON file and returns its content as a dictionary.

    Args:
        json_file (str): Path to the JSON file.

    Returns:
        dict: Parsed JSON content.
    """
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading JSON file {json_file}: {e}", exc_info=True)
        return {}
