"""
This module defines TextModel objects, which are responsible for randomly generating text.

The submodules are as follows:

- **src.TextModel.TextModel**: Has the abstract TextModel class that represents a random text generation model.
- **src.TextModel.MarkovTextModel**: Has the TextModel class that creates text using a Markov model.
- **src.TextModel.MarkovTriads**: Used in `src.TextModel.MarkovTextModel`; represents the underlying table used for these models.
"""

from .TextModel import TextModel
from .MarkovTextModel import MarkovTextModel
