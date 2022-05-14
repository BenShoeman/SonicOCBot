from abc import ABC, abstractmethod
import json
import os
import random
import re
from typing import Callable, Optional, Union

from .SentenceRestorer import SentenceRestorer
import src.Directories as Directories


class TextModel(ABC):
    """Abstract class for pre-trained text generation models."""

    def __init__(self, model_name: str, sentence_restorer: Optional[SentenceRestorer] = None):
        """Create a `TextModel`. Should be called in subclasses to add the `SentenceRestorer`.

        Parameters
        ----------
        sentence_restorer : Optional[SentenceRestorer]
            sentence restorer to use; if None, creates default one to use
        """
        if sentence_restorer is not None:
            self._sentence_restorer = sentence_restorer
        else:
            self._sentence_restorer = SentenceRestorer()

    @abstractmethod
    def get_next_word(self) -> str:
        """Get the next word from the text model based off its current state.

        Returns
        -------
        str
            next word of the text model
        """

    def get_text_block(self, mean_words: Union[int, float] = 20, stdev_words: Union[int, float] = 30) -> str:
        """Get a random block of text from the model.

        Parameters
        ----------
        mean_words : Union[int, float], optional
            average number of words in the paragraph, by default 100
            (this is not strictly the mean as calculation ensures non-zero positive values)
        stdev_words : Union[int, float], optional
            standard deviation of number of words in the paragraph, by default 100

        Returns
        -------
        str
            random block of text from the model
        """
        n_words = max(1, abs(round(random.gauss(mean_words, stdev_words))))
        generated_text = " ".join(self.get_next_word() for _ in range(n_words))
        return self._sentence_restorer.restore_sentences(generated_text)
