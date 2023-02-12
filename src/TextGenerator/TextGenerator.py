from abc import ABC, abstractmethod
from typing import Any, Literal

from src.TextModel import TextModel


class TextGenerator(ABC):
    """Abstract class for a text generator."""

    def __init__(self, model_name: str, model_class: type[TextModel], **kwargs: Any):
        """Create a `TextGenerator`.

        Parameters
        ----------
        model_name : str
            name of the model (usage depends on the model type)
        model_class : type[TextModel]
            class of the TextModel to use

        Other Parameters
        ----------------
        **kwargs : dict
            Other keyword arguments to define how the text model is created; per object specific
        """
        self._text_model: TextModel = model_class(model_name, **kwargs)

    @abstractmethod
    def get_article(self) -> dict[Literal["title", "body"], str]:
        """Get generated text with a title and body as a dict.

        Returns
        -------
        dict[Literal["title", "body"], str]
            dictionary containing the title and body of the article
        """
