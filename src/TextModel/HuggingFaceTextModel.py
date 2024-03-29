import os
import requests
from typing import Any, Optional
from unidecode import unidecode

from .TextModel import TextModel


class HuggingFaceTextModel(TextModel):
    """Text model that uses the Hugging Face inference API to generate text."""

    def __init__(self, model_name: str, max_length: int = 100, strip_last_incomplete_sentence: bool = True, strip_to_closed_quote: bool = False, **kwargs: Any):
        """Create a `HuggingFaceTextModel`. Uses API token in environment variable `HUGGINGFACE_ACCESS_TOKEN`.

        Parameters
        ----------
        model_name : str
            id of the model from https://huggingface.co/models
        max_length: int
            max number of tokens for the model to generate, by default 100
        """
        super().__init__(model_name, **kwargs)
        self.__api_url = "https://api-inference.huggingface.co/models"
        self.__model_id = model_name
        self.__api_token = os.getenv("HUGGINGFACE_ACCESS_TOKEN", "")
        self.max_length = max_length
        self.__strip_last_incomplete_sentence = strip_last_incomplete_sentence
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
        prompt_str = prompt or "Write some text:"
        payload = {
            "inputs": prompt_str,
            "options": {
                "use_cache": False,
                "wait_for_model": True,
            },
            "parameters": {
                "max_length": self.max_length if self.max_length > 0 else 50,
                "repetition_penalty": 7.5,
            },
        }

        headers = {"Authorization": f"Bearer {self.__api_token}"}
        response = requests.post(f"{self.__api_url}/{self.__model_id}", headers=headers, json=payload, timeout=self.__timeout)
        response_json = response.json()

        if not isinstance(response_json, list):
            response.raise_for_status()
        gen_text = unidecode(response_json[0].get("generated_text", "").replace(prompt_str.rstrip(), "")).strip()

        cutoff_index = 0
        if self.__strip_to_closed_quote:
            cutoff_index = max(cutoff_index, gen_text.find('"'), *(gen_text.rfind(f'{punc}"') + 1 for punc in ".,:;?!"))
        if cutoff_index == 0 and self.__strip_last_incomplete_sentence:
            cutoff_index = max(cutoff_index, *(gen_text.rfind(punc) + 1 for punc in ".?!"), *(gen_text.rfind(f'{punc}"') + 2 for punc in ".,:;?!"))

        cleaned_gen_text = gen_text[: cutoff_index if cutoff_index > 0 else len(gen_text)].removesuffix("<|endoftext|>").strip()
        return self._restore_prompt(prompt, cleaned_gen_text)
