import os
import regex
import requests
from threading import Lock
from typing import Any, Optional

from .TextModel import TextModel

api_lock = Lock()


class YouDotComModel(TextModel):
    """Text model that uses the you.com API to generate text."""

    def __init__(self, model_name: str, strip_to_closed_quote: bool = False, **kwargs: Any):
        """Create a `YouDotComModel`. Uses API token in environment variable `YOUDOTCOM_API_KEY`.

        Parameters
        ----------
        model_name : str
            unused as there is a single endpoint
        """
        super().__init__(model_name, **kwargs)
        self.return_prompt = kwargs.get("return_prompt", False)
        self.__api_url = "https://api.betterapi.net/youchat"
        self.__api_key = os.getenv("YOUDOTCOM_API_KEY", "")
        self.__strip_to_closed_quote = strip_to_closed_quote
        self.__timeout = 300

    def get_next_word(self) -> str:
        """Not implemented as the API will return a block of text all at once.

        Raises
        -------
        NotImplementedError
            This uses the API to generate a block of text all at once, so this is not implemented
        """
        raise NotImplementedError("This uses the API to generate a block of text all at once, so this is not implemented.")

    def get_text_block(self, prompt: Optional[str] = None) -> str:
        """Get a random block of text from the model.

        Parameters
        ----------
        prompt : Optional[str]
            prompt to start the model with, or none if starting from empty state

        Returns
        -------
        str
            random block of text from the model
        """
        prompt_str = prompt or "Write some random text."

        # you.com api doesn't work well with concurrent requests, so lock the request call
        with api_lock:
            response = requests.get(
                self.__api_url,
                params={
                    "inputs": prompt_str,
                    "key": self.__api_key,
                },
                timeout=self.__timeout,
            )
        response.raise_for_status()
        content = response.json()
        gen_text = content["generated_text"]

        cutoff_index = 0
        if self.__strip_to_closed_quote:
            cutoff_index = max(cutoff_index, gen_text.find('"'), *(gen_text.rfind(f'{punc}"') + 1 for punc in ".,:;?!"))

        cleaned_gen_text = gen_text[: cutoff_index if cutoff_index > 0 else len(gen_text)].strip()
        # Remove anything where the model indicates it's an AI model
        cleaned_gen_text = regex.sub(
            r"(?<=^\s*|[\.,:;\?!]\s*)(as (an ai|sonic)|starting with the text|.*?(language model|text you provided|start(ing|s) with the text)).*?[\.:\?!]",
            "",
            cleaned_gen_text,
            flags=regex.IGNORECASE,
        )

        return self._restore_prompt(prompt, cleaned_gen_text)
