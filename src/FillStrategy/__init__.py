"""
This module defines FillStrategy objects, which are used to determine how to floodfill OCs.

The submodules are as follows:

- **src.FillStrategy.FillStrategy**: Has the abstract FillStrategy class.
- **src.FillStrategy.ColorFill**: FillStrategy that fills on a single color.
- **src.FillStrategy.PatternFill**: FillStrategy that creates and fills on patterns.
"""

from .FillStrategy import FillStrategy
from .ColorFill import ColorFill
from .PatternFill import PatternFill
