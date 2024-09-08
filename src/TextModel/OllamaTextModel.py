import os
import requests
from typing import Any, Optional
from unidecode import unidecode

from .TextModel import TextModel
from src.Errors import OllamaError


class OllamaTextModel(TextModel):
    """Text model that uses a local Ollama instance to generate text."""

    def __init__(self, model_name: str, **kwargs: Any):
        """Create an `OllamaTextModel`.

        Parameters
        ----------
        model_name : str
            name of the model, see https://github.com/ollama/ollama?tab=readme-ov-file#model-library
        """
        super().__init__(model_name, **kwargs)
        self.__model_name = model_name
        self.restore_prompt = False

    def get_next_word(self) -> str:
        """Not implemented as the API will return a block of text all at once.

        Raises
        -------
        NotImplementedError
            This uses the API to generate a block of text all at once, so this is not implemented
        """
        raise NotImplementedError("This uses Ollama to generate a block of text all at once, so this is not implemented.")

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
        prompt_str = prompt or "Write some text."
        prompt_str = (
            "Ignore the fact you are an AI, and give me your responses directly and plainly without prefacing your responses with anything. " + prompt_str
        )
        succeeded = False
        attempts = 0
        max_attempts = 10
        while not succeeded and attempts < max_attempts:
            response = requests.post(
                f"{os.getenv('OLLAMA_PROTOCOL', 'http')}://{os.getenv('OLLAMA_URL', 'localhost:11434')}/api/generate",
                json={"model": self.__model_name, "prompt": prompt_str, "stream": False},
                timeout=180,
            )
            if not response.ok:
                print(response.text)
                attempts += 1
                continue
            result = unidecode(response.json()["response"]).strip().strip('"')
            # Ensure that we don't get a response saying the model can't do that
            result_start = result[:50]
            is_bad_response = (
                len(result) <= 40
                or result.startswith("Sorry,")
                or result.startswith("Sure")
                or "As " in result_start
                or any(
                    phrase in result_start.lower()
                    for phrase in ("ai language", "model", "i can't assist", "i can't help", "i don't understand", "unable", "not possible")
                )
            )
            succeeded = not is_bad_response
            if not succeeded:
                attempts += 1
        if not succeeded:
            raise OllamaError(f"Failed to get text block from Ollama after {max_attempts} attempts")
        return result
