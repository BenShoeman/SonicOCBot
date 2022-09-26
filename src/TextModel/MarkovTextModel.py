import atexit
import gzip
import numpy as np
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from typing import ClassVar, Optional, Union

from .TextModel import TextModel
from .MarkovTriads import MarkovTriads
import src.Directories as Directories


_rng = np.random.default_rng()


class MarkovTextModel(TextModel):
    """Text model that uses a Markov model to generate text, based off the models generated from `train.py`."""

    MAX_TOKENS_PER_BLOCK: ClassVar[int] = 10000
    """Max tokens per text block in case of a loop in the Markov model."""

    def __init__(self, model_name: str, punc_required: bool = True):
        """Create a `MarkovTextModel`.

        Parameters
        ----------
        model_name : str
            name of the model, which requires the file `models/{model_name}.db.gz`
        punc_required : bool, optional
            whether punctuation is required in this model, by default True
        """
        self.__first_word: Optional[str] = None
        self.__second_word: Optional[str] = None
        self.__punc_required: bool = punc_required
        self.__markov_table = MarkovTriads()
        self.__db_path = Directories.MODELS_DIR / f"{model_name}.db.gz"
        # Don't decompress database right away, only load when necessary
        self.__tmp_path: Optional[str] = None
        self.__engine: Optional[Engine] = None
        # Ensure ungzipped database is deleted on exit
        atexit.register(self.__clean_up)

    def __load_db(self) -> None:
        """Decompress and load the database."""
        self.__tmp_path = f"{self.__db_path}_tmp.db"
        with gzip.open(self.__db_path, "rb") as f_src, open(self.__tmp_path, "wb") as f_dst:
            f_dst.writelines(f_src)
        self.__engine = create_engine(f"sqlite:///{self.__tmp_path}")

    def __clean_up(self) -> None:
        """Delete the ungzipped database file once done."""
        if self.__tmp_path:
            os.remove(self.__tmp_path)

    def get_next_word(self) -> str:
        """Use the Markov model to get the next word.

        Returns
        -------
        str
            next word from the model
        """
        # Load database if not loaded first
        if not self.__engine:
            self.__load_db()
            return self.get_next_word()
        else:
            if self.__second_word:
                if self.__first_word:
                    third_word = self.__markov_table.get_next_token(self.__engine, self.__first_word, self.__second_word)
                else:
                    third_word = self.__markov_table.get_next_token(self.__engine, self.__second_word)
            else:
                third_word = self.__markov_table.get_first_token(self.__engine)
            # Update the Markov model state
            self.__first_word = self.__second_word
            self.__second_word = third_word
            return third_word

    def get_text_block(
        self,
        mean_words: Union[int, float] = 20,
        stdev_words: Union[int, float] = 30,
    ) -> str:
        """Get a random block of text from the model.

        Parameters
        ----------
        mean_words : Union[int, float], optional
            mean number of words in the paragraph, by default 20
        stdev_words : Union[int, float], optional
            standard deviation of number of words in the paragraph, by default 30

        Returns
        -------
        str
            random block of text from the model
        """
        # Reset model state first
        self.__first_word = None
        self.__second_word = None
        n_words = max(1, abs(round(_rng.normal(mean_words, stdev_words))))
        tokens = [self.get_next_word() for _ in range(n_words)]
        # Finish until the end of a sentence, if punctuation is required
        while self.__punc_required and tokens[-1] not in (".", "!", "?") and len(tokens) < self.__class__.MAX_TOKENS_PER_BLOCK:
            tokens.append(self.get_next_word())
        return self.__markov_table.detokenize(tokens)
