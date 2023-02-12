"""
This module defines TextGenerator objects, which are responsible for using TextModels to create text blocks.

The submodules are as follows:

- **src.TextGenerator.TextGenerator**: Has the abstract TextGenerator class that represents a random text generator.
- **src.TextGenerator.FanfictionGenerator**: Has the TextGenerator class that creates fanfiction text.
- **src.TextGenerator.OCBioGenerator**: Has the TextGenerator class that creates OC bio texts.
- **src.TextGenerator.SonicSezGenerator**: Has the TextGenerator class that creates Sonic Says text.
"""

from .TextGenerator import TextGenerator
from .FanfictionGenerator import FanfictionGenerator
from .OCBioGenerator import OCBioGenerator
from .SonicSezGenerator import SonicSezGenerator
