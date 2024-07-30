import json
import logging
import subprocess
from textwrap import dedent
from typing import Any, Optional
from unidecode import unidecode

from .TextModel import TextModel

_logger = logging.getLogger(__name__)


class OllamaTextModel(TextModel):
    """Text model that uses a local Ollama instance to generate text."""

    def __init__(self, model_name: str, **kwargs: Any):
        """Create a `OllamaTextModel`. Uses API token in environment variable `HUGGINGFACE_ACCESS_TOKEN`.

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
        # Specify a format to generate this text in, for easy parsing, and redo it if it doesn't do it right
        prompt_str = (
            "You will format your response in the following JSON list format, strictly following the format and not wrapping it in ```json:\n\n"
            + dedent(
                """
                    [
                        "response 1st paragraph",
                        "response 2nd paragraph",
                        ...
                    ]
                """
            ).strip()
            + "\n\n"
            + prompt_str
        )
        succeeded = False
        max_attempts = 10
        attempts = 0
        while not succeeded and attempts < max_attempts:
            result = subprocess.check_output(["ollama", "run", self.__model_name, prompt_str]).decode().strip()
            try:
                text = json.loads(result)
                assert isinstance(text, list)
                assert all(isinstance(line, str) for line in text)
            except (json.JSONDecodeError, AssertionError):
                _logger.debug("Retrying to get properly formatted text")
                attempts += 1
            else:
                succeeded = True
        if attempts == max_attempts:
            raise Exception("Took too many attempts to get properly formatted text")
        return unidecode("\n\n".join(text))
