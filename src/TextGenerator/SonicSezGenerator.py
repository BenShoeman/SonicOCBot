from typing import Any, Literal, Optional

from .TextGenerator import TextGenerator
from src.TextModel import TextModel
from src.TextModel import MarkovTextModel


class SonicSezGenerator(TextGenerator):
    """Generates Sonic Sez segments using a text model."""

    __DEFAULT_PROMPTS = {
        "HuggingFaceTextModel": 'What is some advice Sonic the Hedgehog would give?\n\n"{salt}',
        "MarkovTextModel": None,
        "OllamaTextModel": (
            'You are Sonic the Hedgehog, a character that loves to act cool and loves to speak using older slang like "radical" and "that\'s way past cool". '
            "Speaking as Sonic, give some advice (in only 1-2 sentences)."
        ),
    }

    def __init__(
        self,
        model_name: str,
        model_class: type[TextModel],
        salt_model_name: Optional[str] = "sonicsez",
        salt_model_class: Optional[type[TextModel]] = MarkovTextModel,
        **kwargs: Any,
    ):
        """Create a `SonicSezGenerator`.

        Parameters
        ----------
        model_name : str
            body text model name
        model_class : type[TextModel]
            class of the text model to use
        salt_model_name : Optional[str]
            salt model name, to salt the main model with (e.g. to help AI model prompts)
        salt_model_class : Optional[type[TextModel]]
            class of the salt model, by default MarkovTextModel

        Other Parameters
        ----------------
        **kwargs : dict
            Other keyword arguments to define what/how much text is generated. Below are the available options:
            - prompts: override for __DEFAULT_PROMPTS
        """
        self._prompt_template = kwargs.get("prompts", {}).get(model_class.__name__, SonicSezGenerator.__DEFAULT_PROMPTS[model_class.__name__])

        self._text_model: TextModel = model_class(model_name, strip_to_closed_quote=True)
        self._text_model.mean_words = 24
        self._text_model.stdev_words = 13
        self._text_model.max_length = 60

        self.__salt_model: Optional[TextModel] = salt_model_class(salt_model_name, punc_required=False) if salt_model_name and salt_model_class else None
        # Always generate 5 tokens as salt
        if self.__salt_model:
            self.__salt_model.mean_words = 5
            self.__salt_model.stdev_words = 0
            self.__salt_model.mean_paragraphs = 1
            self.__salt_model.stdev_paragraphs = 0

    def get_article(self) -> dict[Literal["title", "body"], str]:
        """Get a Sonic Says blurb.

        Returns
        -------
        dict[Literal["title", "body"], str]
            dictionary containing the title and body of the Sonic Says segment
        """
        salt = (self.__salt_model.get_text_block() if self.__salt_model else "").strip()
        body_prompt = self._prompt_template.format(salt=salt).rstrip() if self._prompt_template else None
        body_text = self._text_model.get_text_block(prompt=body_prompt).removeprefix(body_prompt.removesuffix(salt) if body_prompt else "")

        return {"title": "Sonic Says...", "body": body_text if body_text else "You're way past cool!"}
