import json
import os
from typing import Union


def set_environment_from_json(filepath: Union[str, os.PathLike]) -> None:
    """Set environment variables from a JSON file.

    Keys are set in a top_key_lower_key format, such that a JSON file like below:

    ```json
    {
        "app": { "key1": 1, "key2": 2 }
    }
    ```

    Will result in two environment variables set, `app_key1` and `app_key2`, with the values 1 and 2 respectively.

    Parameters
    ----------
    filepath : Union[str, os.PathLike]
        JSON file to read from
    """
    with open(filepath) as f:
        environment_dict = json.load(f)

    for top_key, sub_key_dict in environment_dict.items():
        for sub_key, var_value in sub_key_dict.items():
            os.environ[f"{top_key}_{sub_key}"] = var_value
