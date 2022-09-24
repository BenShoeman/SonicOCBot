import json
from pathlib import Path
from typing import Callable, Union
import yaml


def list_load(filepath: Union[str, Path], fallback_factory: Callable = list) -> list:
    """Load a text file from the path as a list of lines, falling back to a fallback function if it doesn't exist.

    Parameters
    ----------
    filepath : str
        Path of the text file to load
    fallback_factory : Callable, optional
        fallback function to call if file invalid, by default list()

    Returns
    -------
    list
        contents of the file as a list of lines
    """
    if Path(filepath).exists():
        with open(filepath) as f:
            return [line.strip() for line in f.readlines()]
    else:
        print(f"{filepath} does not exist, falling back")
        return fallback_factory()


def json_load(filepath: Union[str, Path], fallback_factory: Callable = dict) -> dict:
    """Load a JSON file from the path, falling back to a fallback function if an invalid file.

    Parameters
    ----------
    filepath : str
        Path of the JSON file to load
    fallback_factory : Callable, optional
        fallback function to call if JSON file invalid, by default dict()

    Returns
    -------
    dict
        dictionary representation of the JSON file
    """
    if Path(filepath).exists():
        try:
            with open(filepath) as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"JSON decode error reading {f}, falling back")
            return fallback_factory()
    else:
        print(f"{filepath} does not exist, falling back")
        return fallback_factory()


def yaml_load(filepath: Union[str, Path], fallback_factory: Callable = dict) -> dict:
    """Load a YAML file from the path, falling back to a fallback function if an invalid file.

    Parameters
    ----------
    filepath : str
        Path of the YAML file to load
    fallback_factory : Callable, optional
        fallback function to call if YAML file invalid, by default dict()

    Returns
    -------
    dict
        dictionary representation of the YAML file
    """
    if Path(filepath).exists():
        try:
            with open(filepath) as f:
                return yaml.safe_load(f)
        except yaml.parser.ParserError:
            print(f"YAML parser error reading {f}, falling back")
            return fallback_factory()
    else:
        print(f"{filepath} does not exist, falling back")
        return fallback_factory()
