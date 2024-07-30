from abc import ABC, abstractmethod
from typing import Any, Optional


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
        mean_words : Union[int, float], optional
            mean number of words in the paragraph, default on a per object basis, by default 20
        stdev_words : Union[int, float], optional
            standard deviation of number of words in the paragraph, default set on a per object basis, by default 10
        mean_paragraphs : Union[int, float], optional
            mean number of paragraphs in generated text, default on a per object basis, by default 1
        stdev_paragraphs : Union[int, float], optional
            standard deviation of number of paragraphs, default set on a per object basis, by default 0
        max_length : int, optional
            max number of words or tokens to generate, only used for some text models; by default -1
        restore_prompt : bool, optional
            whether to return the prompt when generating a text block, by default True
        **kwargs : dict
            Other keyword arguments to define how the text model is created; per object specific
        """
        self.mean_words = kwargs.get("mean_words", 20)
        self.stdev_words = kwargs.get("stdev_words", 10)
        self.mean_paragraphs = kwargs.get("mean_paragraphs", 1)
        self.stdev_paragraphs = kwargs.get("stdev_paragraphs", 0)
        self.max_length = kwargs.get("max_length", -1)
        self.restore_prompt = kwargs.get("restore_prompt", True)

    @abstractmethod
    def get_next_word(self) -> str:
        """Get the next word from the text model based off its current state.

        Returns
        -------
        str
            next word of the text model
        """

    @abstractmethod
    def get_text_block(self, prompt: Optional[str] = None) -> str:
        """Get a random block of text from the model.

        Parameters
        ----------
        prompt : Optional[str]
            prompt to start the model with, or none if starting from empty state

        Returns
        -------
        str
            block of text from the model
        """

    def _restore_prompt(self, prompt: Optional[str], generated_text: str) -> str:
        """Restores a prompt to the generated string if specified in the `restore_prompt` attribute.

        Parameters
        ----------
        prompt : Optional[str]
            prompt to add back to the generated text
        generated_text : str
            generated text from the model

        Returns
        -------
        str
            generated text with prompt prepended if `restore_prompt` is True
        """
        if self.restore_prompt:
            space_between = "" if (not prompt) or (prompt and prompt[-1] in "#$'(-[{") or (generated_text and generated_text[0] in "!')-,.:;?]}") else " "
            return f"{prompt if prompt else ''}{space_between}{generated_text}"
        else:
            return generated_text
