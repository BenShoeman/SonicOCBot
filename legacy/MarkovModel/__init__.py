from abc import ABC, abstractmethod
import random
import re

_EXTRA_PUNCTUATION_REGEX = re.compile(r"[\/#$%\^{}=_`~()\"]")
"""Regex to find unnecessary punctuation and remove it"""

_WORD_REGEX = re.compile(r"([A-Za-z0-9\-\']+|[.,!?&;:])")
"""Regex to extract words from a string"""


class MarkovModel(ABC):
    """Abstract class for Markov models."""

    @abstractmethod
    def add_pair(self, current_word: str, next_word: str) -> None:
        """Create a Markov edge if it doesn't exist, or add 1 to number of instances of that edge if it does.

        Parameters
        ----------
        current_word : str
            first word of the pair
        next_word : str
            second word of the pair
        """

    def add_text(self, text: str) -> None:
        """Train the Markov model with a block of text.

        Parameters
        ----------
        text : str
            text to train Markov model with
        """
        # Remove unnecessary punctuation
        text = _EXTRA_PUNCTUATION_REGEX.sub("", text).strip()
        if text == "":
            return
        # Add period so we know the first word begins a sentence
        text = ". " + text

        words = _WORD_REGEX.findall(text)
        for current_word, next_word in zip(words[:-1], words[1:]):
            self.add_pair(current_word, next_word)

    @abstractmethod
    def get_random_word(self, first_word: bool = False, include_punctuation: bool = False):
        """Get a random word from the Markov model.

        If `first_word` is `True`, this should be the first word of a sentence (i.e., a word preceded by an end punctuation mark).
        If `include_punctuation` is `False`, this should exclude punctuation.

        Parameters
        ----------
        first_word : bool, optional
            whether the random word should be the first word of a sentence, by default False
        include_punctuation : bool, optional
            whether punctuation marks can be included, by default False
        """

    @abstractmethod
    def get_next_words(self, current_word: str) -> list[tuple[str, float]]:
        """Get a list of possible next choices after the current word in the Markov model.

        Possible next choices are in a list of (word, probability) tuples, where sum(probabilities) == 1.

        Parameters
        ----------
        current_word : str
            current word in the Markov model that needs a new word to follow

        Returns
        -------
        list[tuple[str, float]]
            list of possible next choices after `current_word`, in (word, probability) tuples
        """

    def get_random_sentence(self) -> str:
        """Get a random sentence from the Markov model.

        Returns
        -------
        str
            random sentence from the Markov model
        """
        current_word = self.get_random_word(first_word=True)
        sentence = current_word
        while current_word not in [".", "!", "?"]:
            next_word_probabilities = self.get_next_words(current_word)
            if len(next_word_probabilities) > 0:
                n = random.random()
                for word, pr_word in next_word_probabilities:
                    if n < pr_word:
                        current_word = word
                        break
                    n -= pr_word
            else:
                current_word = self.get_random_word(include_punctuation=True)

            # Add a space if current_word is not a punctuation mark
            if current_word not in [".", ",", "!", "?", ";", ":"]:
                sentence += " "

            # Then add the word to the string
            sentence += current_word
        return sentence

    def get_random_paragraph(self, sentences: int = 5) -> str:
        """Get a random paragraph from the Markov model.

        Parameters
        ----------
        sentences : int, optional
            number of sentences in the paragraph, by default 5

        Returns
        -------
        str
            random paragraph from the Markov model
        """
        return " ".join(self.get_random_sentence() for _ in range(sentences))
