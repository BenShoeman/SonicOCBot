"""Constants for getting directory paths relative to the project root.

This module has 7 constants to use. They are:
- **PROJECT_DIR**: Final[Path]<br>
  Project's base directory derived from current file's path.
- **DATA_DIR**: Final[Path]<br>
  Path for text data not associated with models (e.g. name list, animal list, fill info).
- **IMAGES_DIR**: Final[Path]<br>
  Path for Sonic Maker images.
- **MODELS_DIR**: Final[Path]<br>
  Path for text generating models (as of now, only Markov models).
- **FONTS_DIR**: Final[Path]<br>
  Path for bitmap fonts used in OC creation.
- **SONICMAKER_DIR**: Final[Path]<br>
  Path for Sonic Maker creation images.
- **OC_TEMPLATES_DIR**: Final[Path]<br>
  Path for OC template images.
- **POST_TEMPLATES_DIR**: Final[Path]<br>
  Path for post templates (to be implemented).
"""

import os
from pathlib import Path
from typing import Any, Final

_PROJECT_DIR: Final[Path] = Path(os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)))
_DATA_DIR: Final[Path] = _PROJECT_DIR / "data"
_IMAGES_DIR: Final[Path] = _PROJECT_DIR / "images"
_MODELS_DIR: Final[Path] = _PROJECT_DIR / "models"
_FONTS_DIR: Final[Path] = _PROJECT_DIR / "fonts"
_SONICMAKER_DIR: Final[Path] = _IMAGES_DIR / "sonicmaker"
_OC_TEMPLATES_DIR: Final[Path] = _IMAGES_DIR / "octemplate"
_POST_TEMPLATES_DIR: Final[Path] = _IMAGES_DIR / "posttemplate"


def __getattr__(name: str) -> Any:
    attrs = {
        "PROJECT_DIR": _PROJECT_DIR,
        "DATA_DIR": _DATA_DIR,
        "IMAGES_DIR": _IMAGES_DIR,
        "MODELS_DIR": _MODELS_DIR,
        "FONTS_DIR": _FONTS_DIR,
        "SONICMAKER_DIR": _SONICMAKER_DIR,
        "OC_TEMPLATES_DIR": _OC_TEMPLATES_DIR,
        "POST_TEMPLATES_DIR": _POST_TEMPLATES_DIR,
    }
    if name in attrs:
        return attrs[name]
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
