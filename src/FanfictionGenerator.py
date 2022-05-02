import os
import random
from typing import Union

import src.Directories as Directories
from src.TextModel.TextModel import TextModel


def gauss_int(mean: float, stdev: float, min_val: int = 0) -> int:
    """Return a normally distributed random number as an integer, with a specified minimum value.

    Parameters
    ----------
    mean : float
        mean of the normal distribution
    stdev : float
        standard deviation of the normal distribution
    min_val : int, optional
        minimum value of the output, by default 0

    Returns
    -------
    int
        randomly generated output
    """
    return max(min_val, round(random.gauss(mean, stdev)))


class FanfictionGenerator:
    """Generates fanfictions using text models.

    Parameters
    ----------
    body_text_model_model_name : str
        body text model name
    titles_model_model_name : str
        title model name
    model_class : type[TextModel]
        class of the text model to use
    """

    __DEFAULT_KWARGS = {
        "mean_paragraphs": 40,
        "stdev_paragraphs": 30,
        "mean_body_words": 58.5,
        "stdev_body_words": 52,
        "mean_title_words": 3,
        "stdev_title_words": 2,
    }

    def __init__(self, body_text_model_name: str, titles_model_name: str, model_class: type[TextModel], **kwargs):
        self.__body_text_model: TextModel = model_class(body_text_model_name)
        self.__titles_model: TextModel = model_class(titles_model_name)
        self.__mean_paragraphs = kwargs.get("mean_paragraphs", FanfictionGenerator.__DEFAULT_KWARGS["mean_paragraphs"])
        self.__stdev_paragraphs = kwargs.get("stdev_paragraphs", FanfictionGenerator.__DEFAULT_KWARGS["stdev_paragraphs"])
        self.__mean_body_words = kwargs.get("mean_body_words", FanfictionGenerator.__DEFAULT_KWARGS["mean_body_words"])
        self.__stdev_body_words = kwargs.get("stdev_body_words", FanfictionGenerator.__DEFAULT_KWARGS["stdev_body_words"])
        self.__mean_title_words = kwargs.get("mean_title_words", FanfictionGenerator.__DEFAULT_KWARGS["mean_title_words"])
        self.__stdev_title_words = kwargs.get("stdev_title_words", FanfictionGenerator.__DEFAULT_KWARGS["stdev_title_words"])

    def get_fanfiction(self) -> tuple[str, str]:
        """Get a fanfiction with title and body text.

        Returns
        -------
        tuple[str, str]
            title and body text of the fanfiction
        """
        title = self.__titles_model.get_text_block(mean_words=self.__mean_title_words, stdev_words=self.__stdev_title_words)
        body_text = "\n".join(
            self.__body_text_model.get_text_block(mean_words=self.__mean_body_words, stdev_words=self.__stdev_body_words)
            for _ in range(gauss_int(mean=self.__mean_paragraphs, stdev=self.__stdev_paragraphs, min_val=1))
        )
        # Remove punctuation 4/5 of the time, if title ends with punctuation
        if title[-1] in ".,:;!?" and random.random() < 0.8:
            title = title[:-1]
        return title, body_text


class TwitterFanfictionGenerator(FanfictionGenerator):
    """Generates fanfictions with stats suitable for images on Twitter."""

    def __init__(self, body_text_model_name: str, titles_model_name: str, model_class: type[TextModel]):
        super().__init__(
            body_text_model_name, titles_model_name, model_class, mean_paragraphs=3.25, stdev_paragraphs=0.75, mean_body_words=58.5, stdev_body_words=26
        )
