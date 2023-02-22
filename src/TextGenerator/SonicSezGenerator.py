from typing import Literal, Optional

from .TextGenerator import TextGenerator
from src.TextModel import TextModel
from src.TextModel import MarkovTextModel


class SonicSezGenerator(TextGenerator):
    """Generates Sonic Sez segments using a text model."""

    def __init__(
        self,
        model_name: str,
        model_class: type[TextModel],
        salt_model_name: Optional[str] = "sonicsez",
        salt_model_class: Optional[type[TextModel]] = MarkovTextModel,
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
        """
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
        body_prompt = f'What is some advice Sonic the Hedgehog would give?\n\n"{salt}'.rstrip()
        gen_text = self._text_model.get_text_block(prompt=body_prompt)
        space_between = "" if (salt and salt[-1] in "#$'(-[{") or (gen_text and gen_text[0] in "!')-,.:;?]}") else " "
        body_text = f"{salt}{space_between}{gen_text}"

        return {"title": "Sonic Says...", "body": body_text}
