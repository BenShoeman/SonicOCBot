from abc import ABC, abstractmethod
from typing import Any, Union


class TextModel(ABC):
    """Abstract class for pre-trained text generation models."""

    def __init__(self, model_name: str, **kwargs: Any):
        """Create a `TextModel`.

        Parameters
        ----------
        model_name : str
            name of the model (usage depends on the model type)

        Other Parameters
        ----------------
        **kwargs : dict
            Other keyword arguments to define how the text model is created; per object specific
        """

    @abstractmethod
    def get_next_word(self) -> str:
        """Get the next word from the text model based off its current state.

        Returns
        -------
        str
            next word of the text model
        """

    @abstractmethod
    def get_text_block(self, mean_words: Union[int, float] = 0, stdev_words: Union[int, float] = 0) -> str:
        """Get a random block of text from the model.

        Parameters
        ----------
        mean_words : Union[int, float], optional
            mean number of words in the paragraph, default on a per object basis
        stdev_words : Union[int, float], optional
            standard deviation of number of words in the paragraph, default set on a per object basis

        Returns
        -------
        str
            block of text from the model
        """
