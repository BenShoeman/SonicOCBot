import os
import random

import src.Directories as Directories
from src.TextModel import TextModel


class SonicSezGenerator:
    """Generates Sonic Sez segments using a text model."""

    def __init__(self, body_text_model_name: str, model_class: type[TextModel]):
        """Create a `SonicSezGenerator`.

        Parameters
        ----------
        body_text_model_name : str
            body text model name
        model_class : type[TextModel]
            class of the text model to use
        """
        self.__body_text_model: TextModel = model_class(body_text_model_name)

    def get_text(self) -> str:
        """Get a Sonic Says blurb.

        Returns
        -------
        str
            title and body text of the fanfiction
        """
        return self.__body_text_model.get_text_block(mean_words=24, stdev_words=13)
