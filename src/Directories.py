"""Constants for getting directory paths relative to the project root.

This module has 7 constants to use. They are:
- **PROJECT_DIR**: Final[Path]<br>
  Project's base directory derived from current file's path.
- **DATA_DIR**: Final[Path]<br>
  Path for text data not associated with models (e.g. name list, animal list, fill info).
- **FONTS_DIR**: Final[Path]<br>
  Path for bitmap fonts used in OC creation.
- **IMAGES_DIR**: Final[Path]<br>
  Path for Sonic Maker images.
- **MODELS_DIR**: Final[Path]<br>
  Path for text generating models (as of now, only Markov models).
- **TEMPLATES_DIR**: Final[Path]<br>
  Path for post template HTML Jinja templates.
- **SONICMAKER_DIR**: Final[Path]<br>
  Path for Sonic Maker creation images.
- **OC_TEMPLATES_DIR**: Final[Path]<br>
  Path for OC template images.
"""

from pathlib import Path
from typing import Any, Final

_PROJECT_DIR: Final[Path] = Path(__file__).parent.parent.absolute().resolve()
_DATA_DIR: Final[Path] = _PROJECT_DIR / "data"
_FONTS_DIR: Final[Path] = _PROJECT_DIR / "fonts"
_IMAGES_DIR: Final[Path] = _PROJECT_DIR / "images"
_MODELS_DIR: Final[Path] = _PROJECT_DIR / "models"
_TEMPLATES_DIR: Final[Path] = _PROJECT_DIR / "templates"
_SONICMAKER_DIR: Final[Path] = _IMAGES_DIR / "sonicmaker"
_OC_TEMPLATES_DIR: Final[Path] = _IMAGES_DIR / "octemplate"


def __getattr__(name: str) -> Any:
    attrs = {
        "PROJECT_DIR": _PROJECT_DIR,
        "DATA_DIR": _DATA_DIR,
        "FONTS_DIR": _FONTS_DIR,
        "IMAGES_DIR": _IMAGES_DIR,
        "MODELS_DIR": _MODELS_DIR,
        "TEMPLATES_DIR": _TEMPLATES_DIR,
        "SONICMAKER_DIR": _SONICMAKER_DIR,
        "OC_TEMPLATES_DIR": _OC_TEMPLATES_DIR,
    }
    if name in attrs:
        return attrs[name]
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
