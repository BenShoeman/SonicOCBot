import random
from typing import Any, Literal, Optional

from .TextGenerator import TextGenerator
from src.TextModel import TextModel
from src.TextModel import MarkovTextModel


class FanfictionGenerator(TextGenerator):
    """Generates fanfictions using text models."""

    __DEFAULT_KWARGS = {
        "mean_paragraphs": 3.25,
        "stdev_paragraphs": 0.75,
        "mean_body_words": 58.5,
        "stdev_body_words": 26,
        "mean_title_words": 3,
        "stdev_title_words": 2,
        "max_body_length": 250,
    }

    def __init__(
        self,
        model_name: str,
        model_class: type[TextModel],
        title_model_name: str = "fanfics.titles",
        title_model_class: type[TextModel] = MarkovTextModel,
        salt_model_name: Optional[str] = "fanfics.bodies",
        salt_model_class: Optional[type[TextModel]] = MarkovTextModel,
        **kwargs: Any,
    ):
        """Create a `FanfictionGenerator`.

        Parameters
        ----------
        model_name : str
            body text model name
        model_class : type[TextModel]
            class of the text model to use for body text
        title_model_name : str, optional
            title model name, by default "fanfics.titles" for a MarkovTextModel
        title_model_class : type[TextModel], optional
            class of the titles text model, by default MarkovTextModel
        salt_model_name : Optional[str]
            salt model name, to salt the main model with (e.g. to help AI model prompts)
        salt_model_class : Optional[type[TextModel]]
            class of the salt model, by default MarkovTextModel

        Other Parameters
        ----------------
        **kwargs : dict
            Other keyword arguments to define how much text is generated. Below are the available options:
            - mean_paragraphs
            - stdev_paragraphs
            - mean_body_words
            - stdev_body_words
            - max_body_length
            - mean_title_words
            - stdev_title_words
        """
        self._text_model: TextModel = model_class(model_name)
        self._text_model.mean_words = kwargs.get("mean_body_words", FanfictionGenerator.__DEFAULT_KWARGS["mean_body_words"])
        self._text_model.stdev_words = kwargs.get("stdev_body_words", FanfictionGenerator.__DEFAULT_KWARGS["stdev_body_words"])
        self._text_model.mean_paragraphs = kwargs.get("mean_paragraphs", FanfictionGenerator.__DEFAULT_KWARGS["mean_paragraphs"])
        self._text_model.stdev_paragraphs = kwargs.get("stdev_paragraphs", FanfictionGenerator.__DEFAULT_KWARGS["stdev_paragraphs"])
        self._text_model.max_length = kwargs.get("max_body_length", FanfictionGenerator.__DEFAULT_KWARGS["max_body_length"])

        self.__titles_model: TextModel = title_model_class(title_model_name, punc_required=False)
        self.__titles_model.mean_words = kwargs.get("mean_title_words", FanfictionGenerator.__DEFAULT_KWARGS["mean_title_words"])
        self.__titles_model.stdev_words = kwargs.get("stdev_title_words", FanfictionGenerator.__DEFAULT_KWARGS["stdev_title_words"])
        self.__titles_model.mean_paragraphs = 1
        self.__titles_model.stdev_paragraphs = 0

        self.__salt_model: Optional[TextModel] = salt_model_class(salt_model_name, punc_required=False) if salt_model_name and salt_model_class else None
        # Always generate 5 tokens as salt
        if self.__salt_model:
            self.__salt_model.mean_words = 5
            self.__salt_model.stdev_words = 0
            self.__salt_model.mean_paragraphs = 1
            self.__salt_model.stdev_paragraphs = 0

    def get_article(self) -> dict[Literal["title", "body"], str]:
        """Get a fanfiction with a title and body as a dict.

        Returns
        -------
        dict[Literal["title", "body"], str]
            dictionary containing the title and body of the fanfiction
        """
        title = self.__titles_model.get_text_block()
        # Remove title punctuation 4/5 of the time if it ends with punctuation
        if title[-1] in ".,:;!?" and random.random() < 0.8:
            title = title[:-1]

        salt = self.__salt_model.get_text_block() if self.__salt_model else ""
        body_prompt = f"Write a Sonic the Hedgehog fanfiction.\n\nTitle: {title}\n\n{salt}".rstrip()
        body_text = f"{salt.strip()} {self._text_model.get_text_block(prompt=body_prompt)}"

        return {"title": title, "body": body_text}
