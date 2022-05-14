"""Constants for getting directory paths relative to the project root.

This module has 7 constants to use. They are:
- **PROJECT_DIR**: Final[str]<br>
  Project's base directory derived from current file's path.
- **DATA_DIR**: Final[str]<br>
  Path for text data not associated with models (e.g. name list, animal list, fill info).
- **IMAGES_DIR**: Final[str]<br>
  Path for Sonic Maker images.
- **MODELS_DIR**: Final[str]<br>
  Path for text generating models (as of now, only Markov models).
- **FONTS_DIR**: Final[str]<br>
  Path for bitmap fonts used in OC creation.
- **SONICMAKER_DIR**: Final[str]<br>
  Path for Sonic Maker creation data, including images and fill info.
- **TEMPLATES_DIR**: Final[str]<br>
  Path for templates (including fill info).
"""

import os
import sys
from typing import Final

_PROJECT_DIR: Final[str] = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
_DATA_DIR: Final[str] = os.path.join(_PROJECT_DIR, "data")
_IMAGES_DIR: Final[str] = os.path.join(_PROJECT_DIR, "images")
_MODELS_DIR: Final[str] = os.path.join(_PROJECT_DIR, "models")
_FONTS_DIR: Final[str] = os.path.join(_PROJECT_DIR, "fonts")
_SONICMAKER_DIR: Final[str] = os.path.join(_PROJECT_DIR, "sonicmaker")
_TEMPLATES_DIR: Final[str] = os.path.join(_PROJECT_DIR, "templates")


def __getattr__(name):
    attrs = {
        "PROJECT_DIR": _PROJECT_DIR,
        "DATA_DIR": _DATA_DIR,
        "IMAGES_DIR": _IMAGES_DIR,
        "MODELS_DIR": _MODELS_DIR,
        "FONTS_DIR": _FONTS_DIR,
        "SONICMAKER_DIR": _SONICMAKER_DIR,
        "TEMPLATES_DIR": _TEMPLATES_DIR,
    }
    if name in attrs:
        return attrs[name]
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
