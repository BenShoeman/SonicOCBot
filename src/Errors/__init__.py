"""
This module provides commonly used errors across the project.
"""


class OllamaError(Exception):
    """Exception raised by errors raised from Ollama text generation."""

    def __init__(self, model_name: str, attempts: int = 0) -> None:
        message = f"Failed to get text block from Ollama model {model_name}"
        if attempts > 0:
            message += f" after {attempts} attempts"
        super().__init__(message)
