import regex
from textwrap import dedent
from typing import Any, Literal

from .TextGenerator import TextGenerator
from src.TextModel import TextModel


class OCBioGenerator(TextGenerator):
    """Generates OC bios using a text model."""

    __DEFAULT_PROMPTS = {
        "HuggingFaceTextModel": dedent(
            """
                Write a Sonic OC bio for:

                Name: {name}
                Species: {species}
                Gender: {gender}
                Age: {age}
                Personality: {personalities}
                Skills: {skills}
                Backstory:
            """
        ).strip(),
        "MarkovTextModel": None,
        "YouDotComModel": dedent(
            """
                Write a backstory (1 paragraph max) for the following Sonic OC:

                Name: {name}
                Species: {species}
                Gender: {gender}
                Age: {age}
                Personality: {personalities}
                Skills: {skills}
            """
        ).strip(),
    }

    def __init__(
        self,
        model_name: str,
        model_class: type[TextModel],
        oc: Any,
        **kwargs: Any,
    ):
        """Create an `OCBioGenerator`.

        Parameters
        ----------
        model_name : str
            body text model name
        model_class : type[TextModel]
            class of the text model to use
        oc : OC
            generated OC to use

        Other Parameters
        ----------------
        **kwargs : dict
            Other keyword arguments to define what/how much text is generated. Below are the available options:
            - prompts: override for __DEFAULT_PROMPTS
        """
        self._prompt_template = kwargs.get("prompts", {}).get(model_class.__name__, OCBioGenerator.__DEFAULT_PROMPTS[model_class.__name__])

        self._text_model: TextModel = model_class(model_name)
        self._text_model.mean_words = 42
        self._text_model.stdev_words = 20
        self._text_model.max_length = 150
        self.__oc = oc

    def get_article(self) -> dict[Literal["title", "body"], str]:
        """Get an OC character description.

        Returns
        -------
        dict[Literal["title", "body"], str]
            dictionary containing the title and body of the OC description
        """
        body_prompt = (
            self._prompt_template.format(
                name=self.__oc.name,
                species=self.__oc.species.title(),
                gender=self.__oc.gender_full.title(),
                age=self.__oc.age,
                personalities=", ".join(self.__oc.personalities),
                skills=", ".join(self.__oc.skills),
            )
            if self._prompt_template
            else None
        )
        body_text = self._text_model.get_text_block(prompt=body_prompt)
        # Some text cleanup if model ends up regurgitating prompt back, but slightly modified
        body_text = regex.sub("^(Write a Sonic OC bio for|Name|Species|Gender|Age|Personality|Skills):.*?$", "", body_text, flags=regex.MULTILINE)
        body_text = regex.sub(r"^(Backstory|Bio):\s*(?=.*?$)", "", body_text, flags=regex.MULTILINE)
        body_text = regex.sub(r"\n\n+", "\n\n", body_text).strip()
        # Force capitalization on first sentence if it's not capitalized, and if we got nothing from the model then just add filler text
        body_text = body_text[0].upper() + body_text[1:] if body_text else "*UNDER CONSTRUCTION*"
        return {"title": f"{self.__oc.name} the {self.__oc.species.title()}", "body": body_text}
