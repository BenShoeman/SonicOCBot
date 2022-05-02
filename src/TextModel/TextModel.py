from abc import ABC, abstractmethod
import json
import nltk
from nnsplit import NNSplit
import os
import random
import re
from typing import Callable, Optional, Union

import src.Directories as Directories

nltk.download("averaged_perceptron_tagger", quiet=True)
nltk.download("punkt", quiet=True)


def _json_load_or_fallback(filepath: str, fallback_factory: Callable) -> dict:
    if os.path.exists(filepath):
        try:
            with open(filepath) as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"JSON decode error reading {f}, falling back to empty dict")
            return fallback_factory()
    else:
        print(f"{f} does not exist, falling back to empty dict")
        return fallback_factory()


def _read_list_to_regex(filepath: Union[str, os.PathLike]) -> tuple[re.Pattern, dict[str, str]]:
    """Read the file into a regex that matches on any line in the input file, plus a corrections map.

    Parameters
    ----------
    filepath : Union[str, os.PathLike]
        file to open

    Returns
    -------
    tuple[re.Pattern, dict[str, str]]
        regex that matches on any line in the input file, plus a corrections map
    """
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            lines = [line.strip() for line in f.readlines()]
        rgx = re.compile(f"\\b(?:{'|'.join(re.escape(line) for line in lines)})\\b", flags=re.IGNORECASE)
        corrections = {line.lower(): line for line in lines}
        return rgx, corrections
    else:
        print(f"Error reading {filepath}; returning never-matching regex")
        return re.compile(r"^j\bx"), {}


class TextModel(ABC):
    """Abstract class for pre-trained text generation models.

    Parameters
    ----------
    model_name : str
        name of the model to load it
    """

    sentence_splitter = NNSplit.load("en")
    punctuation_probabilities = _json_load_or_fallback(os.path.join(Directories.MODELS_DIR, "punctuation.probabilities.json"), dict)
    proper_nouns_regex, proper_nouns_map = _read_list_to_regex(os.path.join(Directories.DATA_DIR, "dictionary.propernouns.txt"))

    @abstractmethod
    def __init__(self, model_name: str):
        """Text model constructor"""

    @abstractmethod
    def get_next_word(self) -> str:
        """Get the next word from the text model based off its current state.

        Returns
        -------
        str
            next word of the text model
        """

    def _restore_proper_nouns(self, text: str) -> str:
        """Based off the class's proper nouns list, restore uncapitalized words in the input string.

        Parameters
        ----------
        text : str
            input string to restore proper nouns for

        Returns
        -------
        str
            string with restored proper nouns
        """
        return TextModel.proper_nouns_regex.sub(lambda m: TextModel.proper_nouns_map.get(m.group(), m.group().title()), text)

    def _convert_to_sentence(self, text: str, capitalize: bool = True) -> str:
        """Convert the inputted text into a sentence with punctuation and capitalization.

        Parameters
        ----------
        text : str
            input text to make into a sentence
        capitalize: bool
            whether to capitalize the first word of the sentence

        Returns
        -------
        str
            input text as a sentence
        """
        # Pick a random punctuation mark to end the sentence with, based on the last word of sentence's part of speech
        sentence = str(text).strip()
        last_pos = nltk.pos_tag(nltk.word_tokenize(sentence))[-1][1]
        punc_marks = TextModel.punctuation_probabilities.get(last_pos, {})
        if len(punc_marks) > 0:
            punc_mark_probs = [(mark, pr) for mark, pr in punc_marks.items()]
            marks = [mark for mark, pr in punc_mark_probs]
            probs = [pr for mark, pr in punc_mark_probs]
            punc_mark = random.choices(marks, probs, k=1)[0]
        else:
            punc_mark = ""
        # Add punctuation mark and capitalize first word of sentence, if applicable
        if capitalize:
            return sentence[0].upper() + sentence[1:] + punc_mark
        else:
            return sentence + punc_mark

    def get_text_block(self, mean_words: Union[int, float] = 20, stdev_words: Union[int, float] = 30) -> str:
        """Get a random block of text from the model.

        Parameters
        ----------
        mean_words : Union[int, float], optional
            average number of words in the paragraph, by default 100
            (this is not strictly the mean as calculation ensures non-zero positive values)
        stdev_words : Union[int, float], optional
            standard deviation of number of words in the paragraph, by default 100

        Returns
        -------
        str
            random block of text from the model
        """
        # sonicsez: mean 32 stdev 18
        n_words = max(1, abs(round(random.gauss(mean_words, stdev_words))))
        generated_text = self._restore_proper_nouns(" ".join(self.get_next_word() for _ in range(n_words)))
        sentences = TextModel.sentence_splitter.split([generated_text])[0]
        punctuated_sentences = []
        last_punc_mark = " "
        for sentence in sentences:
            converted_sentence = self._convert_to_sentence(sentence, capitalize=(last_punc_mark not in ",;:"))
            last_punc_mark = converted_sentence[-1]
            punctuated_sentences.append(converted_sentence)
        text_block = " ".join(punctuated_sentences)
        # Replace final punctuation if not a period, exclamation point, or question mark
        if text_block[-1] not in ".!?":
            text_block = text_block[:-1] + "."
        return text_block
