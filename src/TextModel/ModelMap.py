"""Contains constants mapping model names to model classes and their probabilities of being used.

This module has 2 constants to use. They are:
- **MODEL_CLASSES**: Final[dict[str, type[TextModel]]]<br>
  Map of model type names to their classes.
- **MODEL_NAMES**: Final[dict[str, Union[str, dict[str, str]]]]<br>
  Map of model type names to the model name to use for that model.
- **MODEL_PROBABILITIES**: Final[dict[str, float]]<br>
  Map of model type names to their probabilities of using them.
"""

from typing import Any, Final, Union

from src.TextModel import TextModel, HuggingFaceTextModel, MarkovTextModel, OllamaTextModel

_MODEL_CLASSES: Final[dict[str, type[TextModel]]] = {
    "gpt-neo-125m": HuggingFaceTextModel,
    "gpt-neo-1.3B": HuggingFaceTextModel,
    "Markov": MarkovTextModel,
    "Ollama": OllamaTextModel,
}
_MODEL_NAMES: Final[dict[str, Union[str, dict[str, str]]]] = {
    "gpt-neo-125m": "EleutherAI/gpt-neo-125m",
    "gpt-neo-1.3B": "EleutherAI/gpt-neo-1.3B",
    "Markov": {
        "fanfic": "fanfics.bodies",
        "oc": "ocdescriptions.{gender}",
        "sonicsez": "sonicsez",
    },
    "Ollama": "phi3",
}
_MODEL_PROBABILITIES: Final[dict[str, float]] = {
    "Markov": 0.34,
    "Ollama": 0.66,
}


def __getattr__(name: str) -> Any:
    attrs = {
        "MODEL_CLASSES": _MODEL_CLASSES,
        "MODEL_NAMES": _MODEL_NAMES,
        "MODEL_PROBABILITIES": _MODEL_PROBABILITIES,
    }
    if name in attrs:
        return attrs[name]
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
