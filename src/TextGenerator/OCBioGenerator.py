import random
import re
from textwrap import dedent
from typing import Any, Literal

from .TextGenerator import TextGenerator
from src.TextModel import TextModel


class OCBioGenerator(TextGenerator):
    """Generates OC bios using a text model."""

    def __init__(
        self,
        model_name: str,
        model_class: type[TextModel],
        oc: Any,
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
        """
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
        body_prompt = dedent(
            f"""
                Write a Sonic OC bio for:

                Name: {self.__oc.name}
                Species: {self.__oc.species.title()}
                Gender: {self.__oc.gender_full.title()}
                Age: {self.__oc.age}
                {"Personality" if random.random() < 0.5 else "Traits"}: {', '.join(self.__oc.personalities)}
                Skills: {', '.join(self.__oc.skills)}
                {"Backstory" if random.random() < 0.5 else "Bio"}:
            """
        ).strip()
        body_text = self._text_model.get_text_block(prompt=body_prompt)
        # Some text cleanup if model ends up regurgitating prompt back, but slightly modified
        body_text = re.sub(
            "^(Write a Sonic OC bio for|Name|Species|Gender|Age|Personality|Traits|Skills|Backstory|Bio):.*?$", "", body_text, flags=re.MULTILINE
        )
        body_text = re.sub(r"\n\n+", "\n\n", body_text).strip()
        # Force capitalization on first sentence if it's not capitalized, and if we got nothing from the model then just add filler text
        body_text = body_text[0].upper() + body_text[1:] if body_text else "*UNDER CONSTRUCTION*"
        return {"title": f"{self.__oc.name} the {self.__oc.species.title()}", "body": body_text}
