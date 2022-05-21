import json
import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer
import os
import random
import re
from typing import Callable, Optional, Union

import src.Directories as Directories

nltk.download("averaged_perceptron_tagger", quiet=True)
nltk.download("punkt", quiet=True)


def _gauss_int(mean: float, stdev: float, min_val: int = 0) -> int:
    return max(min_val, round(random.gauss(mean, stdev)))


def _list_load_or_fallback(filepath: str, fallback_factory: Callable) -> list:
    if os.path.exists(filepath):
        with open(filepath) as f:
            return [line.strip() for line in f.readlines()]
    else:
        return fallback_factory()


def _json_load_or_fallback(filepath: str, fallback_factory: Callable) -> dict:
    if os.path.exists(filepath):
        try:
            with open(filepath) as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"JSON decode error reading {filepath}, falling back to empty dict")
            return fallback_factory()
    else:
        print(f"{filepath} does not exist, falling back to empty dict")
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


class SentenceRestorer:
    """Object that restores sentences in unpunctuated text."""

    _DEFAULT_STR_KWARGS: dict[str, str] = {
        "sent_seqs_file": os.path.join(Directories.MODELS_DIR, "sentence.sequences.txt"),
        "punc_probs_file": os.path.join(Directories.MODELS_DIR, "punctuation.probabilities.json"),
        "proper_nouns_file": os.path.join(Directories.DATA_DIR, "dictionary.propernouns.txt"),
    }

    _DEFAULT_FLOAT_KWARGS: dict[str, float] = {
        "mean_words_per_sentence": 10.5,
        "stdev_words_per_sentence": 4.5,
    }

    def __init__(self, sent_seqs_file: Optional[str] = None, punc_probs_file: Optional[str] = None, proper_nouns_file: Optional[str] = None, **kwargs):
        """Create a `SentenceRestorer`.

        Parameters
        ----------
        sent_seqs_file : Optional[str], optional
            file in `models` directory that contains possible sentence sequence types; if None, uses `sentences.sequences.txt`
        punc_probs_file : Optional[str], optional
            file in `models` directory that contains probabilities of punctuation marks after specific parts of speech; if None, uses
            `punctuation.probabilities.json`
        proper_nouns_file : Optional[str], optional
            file in `data` directory that contains a list of proper nouns/adjectives; if None, uses `dictionary.propernouns.txt`

        Other Parameters
        ----------------
        **kwargs : dict
            other parameters to fine tune how the `SentenceRestorer` works, with below available arguments:
            - mean_words_per_sentence
            - stdev_words_per_sentence
        """
        sent_seqs_file = sent_seqs_file or str(SentenceRestorer._DEFAULT_STR_KWARGS["sent_seqs_file"])
        punc_probs_file = punc_probs_file or str(SentenceRestorer._DEFAULT_STR_KWARGS["punc_probs_file"])
        proper_nouns_file = proper_nouns_file or str(SentenceRestorer._DEFAULT_STR_KWARGS["proper_nouns_file"])
        self._sent_seqs = [tuple(seq.split(",")) for seq in _list_load_or_fallback(os.path.join(Directories.MODELS_DIR, sent_seqs_file), list)]
        self._punc_probs = _json_load_or_fallback(os.path.join(Directories.MODELS_DIR, punc_probs_file), dict)
        self._proper_nouns_regex, self._proper_nouns_map = _read_list_to_regex(os.path.join(Directories.DATA_DIR, proper_nouns_file))
        self._mean_words_per_sentence = kwargs.get("mean_words_per_sentence") or SentenceRestorer._DEFAULT_FLOAT_KWARGS["mean_words_per_sentence"]
        self._stdev_words_per_sentence = kwargs.get("stdev_words_per_sentence") or SentenceRestorer._DEFAULT_FLOAT_KWARGS["stdev_words_per_sentence"]

    def _restore_proper_nouns(self, text: str) -> str:
        return self._proper_nouns_regex.sub(lambda m: self._proper_nouns_map.get(m.group(), m.group().title()), text)

    def _segment_and_capitalize_sentences(self, text: str) -> list[str]:
        # Helper function to capitalize
        def capitalize(text: str) -> str:
            return text[0].upper() + text[1:]

        pos_tags = nltk.pos_tag(nltk.word_tokenize(capitalize(self._restore_proper_nouns(text))))
        word_detokenizer = TreebankWordDetokenizer()
        sentences = []
        while len(pos_tags) > 0:
            # Pull random amount of words and see if it matches a known sequence
            len_sentence = min(len(pos_tags), _gauss_int(mean=self._mean_words_per_sentence, stdev=self._stdev_words_per_sentence, min_val=1))
            seq = pos_tags[:len_sentence]
            seq_pos = tuple(tag[1] for tag in seq)
            while seq_pos not in self._sent_seqs and len_sentence > 1:
                len_sentence -= 1
                seq = pos_tags[:len_sentence]
                seq_pos = tuple(tag[1] for tag in seq)
            sentences.append(word_detokenizer.detokenize(tag[0] for tag in seq))
            # Get parts of speech for next word, and capitalize the first word to get proper tags
            next_words = [tag[0] for tag in pos_tags[len_sentence:]]
            if len(next_words) > 0:
                next_words[0] = capitalize(next_words[0])
            pos_tags = nltk.pos_tag(next_words)
        return sentences

    def _punctuate_sentences(self, sentences: list[str]) -> list[str]:
        new_sentences = []
        last_punc_mark = "."
        for sentence in sentences:
            # Pick a random punctuation mark to end the sentence with, based on the last word of sentence's part of speech
            last_pos = nltk.pos_tag(nltk.word_tokenize(sentence))[-1][1]
            punc_marks = self._punc_probs.get(last_pos, {})
            if len(punc_marks) > 0:
                punc_mark_probs = [(mark, pr) for mark, pr in punc_marks.items()]
                marks = [mark for mark, pr in punc_mark_probs]
                probs = [pr for mark, pr in punc_mark_probs]
                punc_mark = random.choices(marks, probs, k=1)[0]
            else:
                punc_mark = ""
            # Add punctuation mark and decapitalize first word of sentence, if applicable
            if last_punc_mark in ",;:":
                new_sentences.append(self._restore_proper_nouns(sentence[0].lower() + sentence[1:]) + punc_mark)
            else:
                new_sentences.append(sentence + punc_mark)
            last_punc_mark = punc_mark
        return new_sentences

    def restore_sentences(self, text: str) -> str:
        """Restore sentences in the given text, with punctuation and capitalization.

        Parameters
        ----------
        text : str
            text to restore

        Returns
        -------
        str
            a string with corrected punctuation and capitalization
        """
        sentences = self._segment_and_capitalize_sentences(text)
        sentences = self._punctuate_sentences(sentences)
        text_block = " ".join(sentences)
        # Minor fixes
        text_block = re.sub("(?:\.{1,3}|[,:;!?])? ('s|'m|'re|'ll|'d|'ve|[Nn]'t)", lambda m: m.groups()[0].lower(), text_block)
        text_block = re.sub(" '(?:\.{1,3}|[,:;!?])", "", text_block)
        # Replace final punctuation if not a period, exclamation point, or question mark
        if text_block[-1] not in ".!?":
            text_block = text_block[:-1] + "."
        return text_block
