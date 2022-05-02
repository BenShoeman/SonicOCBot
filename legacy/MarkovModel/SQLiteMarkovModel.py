from os import PathLike
import random
import sqlite3
from typing import Union

from src.legacy.MarkovModel import MarkovModel


class SQLiteMarkovModel(MarkovModel):
    """`MarkovModel` implemented using local SQLite3 database.

    Parameters
    ----------
    db_filename : Union[str, PathLike]
        path to database file, can be a new file or existing one
    """

    __COMMIT_INTERVAL = 5000
    """The amount of words to put in before committing DB transactions"""

    def __init__(self, db_filename: Union[str, PathLike]):
        self.__conn = sqlite3.connect(db_filename)
        # Create Markov edges table if it doesn't exist
        cur = self.__conn.cursor()
        cur.execute("create table if not exists markov_edges (curr_word varchar, " "next_word varchar, instances int);")
        self.__conn.commit()

        # Words added in a single add_text call
        self.__add_count = 0

    def __del__(self):
        self.__conn.close()

    def add_pair(self, current_word: str, next_word: str) -> None:
        """Implements `add_pair` in `MarkovModel` using SQLite transactions.

        Parameters
        ----------
        current_word : str
            first word of the pair
        next_word : str
            second word of the pair
        """
        try:
            # Escape single quotes
            current_word = current_word.replace("'", "''")
            next_word = next_word.replace("'", "''")

            cur = self.__conn.cursor()
            # Try to find this edge
            cur.execute(f"select * from markov_edges where curr_word='{current_word}' and next_word='{next_word}';")
            # If edge doesn't exist, add it
            if len(cur.fetchall()) == 0:
                cur.execute(f"insert into markov_edges (curr_word, next_word, instances) values ('{current_word}', '{next_word}', 1);")
            # Otherwise increment number of instances
            else:
                cur.execute(f"update markov_edges set instances = instances + 1 where curr_word='{current_word}' and next_word='{next_word}';")

            self.__add_count = (self.__add_count + 1) % SQLiteMarkovModel.__COMMIT_INTERVAL
            if self.__add_count == SQLiteMarkovModel.__COMMIT_INTERVAL - 1:
                self.__conn.commit()
        except sqlite3.OperationalError as e:
            print("Error:", e)
            self.__conn.rollback()
            self.__add_count = 0

    def add_text(self, text: str) -> None:
        """Same behavior as `add_text` in `MarkovModel`, but also commits the transaction at the end.

        Parameters
        ----------
        text : str
            text to train Markov model with
        """
        super().add_text(text)
        self.__conn.commit()
        self.__add_count = 0

    def get_random_word(self, first_word: bool = False, include_punctuation: bool = False):
        """Implements `get_random_word` in `MarkovModel` by querying the SQLite database.

        Parameters
        ----------
        first_word : bool, optional
            whether the random word should be the first word of a sentence, by default False
        include_punctuation : bool, optional
            whether punctuation marks can be included, by default False
        """
        cur = self.__conn.cursor()
        condition = ""
        if first_word:
            condition += " where curr_word in ('.','!','?')"
        if not include_punctuation:
            if first_word:
                condition += " and"
            else:
                condition += " where"
            condition += " next_word not in ('.',',','!','?',';',':')"
        cur.execute("select distinct next_word from markov_edges" + condition + ";")
        return random.choice(cur.fetchall())[0]

    def get_next_words(self, current_word: str) -> list[tuple[str, float]]:
        """Implements `get_next_words` in `MarkovModel` by querying the SQLite database.

        Parameters
        ----------
        current_word : str
            current word in the Markov model that needs a new word to follow

        Returns
        -------
        list[tuple[str, float]]
            list of possible next choices after `current_word`, in (word, probability) tuples
        """
        cur = self.__conn.cursor()
        cur.execute(
            "select next_word, cast(instances as float) / (select "
            "sum(instances) from markov_edges where curr_word='{0}') as "
            "probability from markov_edges where curr_word='{0}';".format(current_word.replace("'", "''"))
        )
        return cur.fetchall()
