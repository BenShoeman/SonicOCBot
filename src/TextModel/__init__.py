"""
This module defines TextModel objects, which are responsible for randomly generating text.

The submodules are as follows:

- **src.TextModel.TextModel**: Has the abstract TextModel class that represents a random text generation model.
- **src.TextModel.HuggingFaceTextModel**: Has the TextModel class that creates text using the Hugging Face inference API.
- **src.TextModel.MarkovTextModel**: Has the TextModel class that creates text using a Markov model.
- **src.TextModel.MarkovTriads**: Used in `src.TextModel.MarkovTextModel`; represents the underlying table used for these models.
- **src.TextModel.ModelMap**: Contains constants mapping model type names to the model classes and their probabilities of being used.
- **src.TextModel.OllamaTextModel**: Has the TextModel class that creates text using Ollama.
"""

from .TextModel import TextModel
from .HuggingFaceTextModel import HuggingFaceTextModel
from .MarkovTextModel import MarkovTextModel
from .OllamaTextModel import OllamaTextModel
