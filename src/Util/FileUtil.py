import base64
import logging
import mimetypes
import json
from pathlib import Path
from typing import Callable, Union
import yaml


_logger = logging.getLogger(__name__)


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
    if Path(filepath).is_file():
        with open(filepath) as f:
            return [line.strip() for line in f.readlines()]
    else:
        _logger.warn(f"{filepath} does not exist, falling back")
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
    if Path(filepath).is_file():
        try:
            with open(filepath) as f:
                return json.load(f)
        except json.JSONDecodeError:
            _logger.warn(f"JSON decode error reading {f}, falling back")
            return fallback_factory()
    else:
        _logger.warn(f"{filepath} does not exist, falling back")
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
    if Path(filepath).is_file():
        try:
            with open(filepath) as f:
                return yaml.safe_load(f)
        except yaml.parser.ParserError:
            _logger.warn(f"YAML parser error reading {f}, falling back")
            return fallback_factory()
    else:
        _logger.warn(f"{filepath} does not exist, falling back")
        return fallback_factory()


def file_to_data_url(filepath: Union[str, Path]) -> str:
    """Returns a data URL of the file.

    Parameters
    ----------
    filepath : Union[str, Path]
        Path of file to make a data URL of

    Returns
    -------
    str
        data URL of the file
    """
    filepath = Path(filepath)
    mime_type, encoding = mimetypes.guess_type(filepath)
    if filepath.is_file():
        b64_text = base64.b64encode(filepath.read_bytes()).decode("utf-8")
        return f"data:{mime_type};base64,{b64_text}"
    else:
        _logger.warn(f"{filepath} does not exist, returning empty string")
        return ""
