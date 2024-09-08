import argparse
from dataclasses import dataclass, field
import gzip
from itertools import groupby
import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer
import numpy as np
import os
from sqlalchemy import create_engine, Column, Integer, String, and_, select, delete, func
from sqlalchemy.engine import Engine, Row
from typing import Optional

import src.Directories as Directories
from src.UpsertTable import UpsertTable

nltk.download("punkt", quiet=True)

_rng = np.random.default_rng()


@dataclass
class MarkovTriads(UpsertTable):
    """Table that contains Markov model triads."""

    table_name: str = field(default="markov_triads")
    columns: list[Column] = field(
        default_factory=lambda: [
            Column("first_token", String, primary_key=True, nullable=False),
            Column("second_token", String, primary_key=True, nullable=False),
            Column("third_token", String, primary_key=True, nullable=False),
            Column("occurrences", Integer, default=0),
        ]
    )

    def upsert_triads(self, engine: Engine, text: str, overwrite_probs: bool = False) -> None:
        """Upsert Markov triads into the database from the inputted text.

        Parameters
        ----------
        engine : Engine
            SQLAlchemy engine to upsert triads into
        text : str
            text to create Markov triads from
        overwrite_probs : bool, optional
            whether to overwrite the weights in the database or to just add them, by default False

        Raises
        ------
        ValueError
            raised if input text is less than 3 tokens
        """
        tokens = nltk.word_tokenize(text)
        if len(tokens) < 3:
            raise ValueError("Input text has less than 3 tokens; triads cannot be made")
        records = [
            {
                "first_token": token,
                "second_token": tokens[(i + 1) % len(tokens)],
                "third_token": tokens[(i + 2) % len(tokens)],
                "occurrences": 1,
            }
            for i, token in enumerate(tokens)
        ]
        group_key = lambda rec: (rec["first_token"], rec["second_token"], rec["third_token"])
        grouped_iter = groupby(sorted(records, key=group_key), key=group_key)
        grouped_records = [
            {
                "first_token": key[0],
                "second_token": key[1],
                "third_token": key[2],
                "occurrences": sum(rec["occurrences"] for rec in group),
            }
            for key, group in grouped_iter
        ]
        self.upsert(engine, grouped_records, upsert_type="overwrite" if overwrite_probs else "add")
        # Delete triads where all 3 words are the same, to avoid repeating symbols too much
        engine.execute(
            delete(self.table_def).where(
                and_(
                    self.table_def.columns.first_token == self.table_def.columns.second_token,
                    self.table_def.columns.second_token == self.table_def.columns.third_token,
                )
            )
        )

    def remove_uncommon_tokens(self, engine: Engine, uncommon_threshold: int = 5) -> None:
        """Remove uncommon tokens from the table.

        Parameters
        ----------
        engine : Engine
            SQLAlchemy engine with table to remove uncommon tokens from
        """
        engine.execute(
            delete(self.table_def).where(
                self.table_def.columns.first_token.in_(
                    select(self.table_def.columns.first_token)
                    .distinct()
                    .group_by(self.table_def.columns.first_token)
                    .having(func.count(self.table_def.columns.first_token) <= uncommon_threshold)
                )
            )
        )

    def _choose_word_from_rows(self, rows: list[Row]) -> Optional[str]:
        """Choose a word from rows of (word, weight).

        Parameters
        ----------
        rows : list[Row]
            list of queried rows with words and weights

        Returns
        -------
        str
            chosen word
        """
        if len(rows) == 0:
            return None
        words, weights = tuple(zip(*rows))
        probs = np.asarray(weights)
        probs = probs / probs.sum()
        return _rng.choice(words, p=probs)

    def get_first_token(self, engine: Engine) -> str:
        """Return the first token for a generated sentence.

        Parameters
        ----------
        engine : Engine
            SQLAlchemy engine to query from

        Returns
        -------
        str
            first generated token
        """
        chosen_token: Optional[str] = None
        while not chosen_token:
            sel_stmt = (
                select(self.table_def.columns.third_token, func.sum(self.table_def.columns.occurrences))
                .where(self.table_def.columns.second_token.in_((".", "!", "?")))
                .group_by(self.table_def.columns.third_token)
            )
            rows = engine.execute(sel_stmt).fetchall()
            chosen_token = self._choose_word_from_rows(rows)
        return chosen_token

    def get_next_token(self, engine: Engine, first_token: str, second_token: Optional[str] = None) -> str:
        """Return the next token for a generated sentence.

        Parameters
        ----------
        engine : Engine
            SQLAlchemy engine to query from
        first_token : str
            first token to check in model
        second_token : Optional[str], optional
            second token to check in model, by default None

        Returns
        -------
        str
            next generated token
        """
        # Treat as 1-gram Markov model if only first_token provided, otherwise 2-gram
        if not second_token:
            sel_stmt = (
                select(self.table_def.columns.third_token, func.sum(self.table_def.columns.occurrences))
                .where(self.table_def.columns.second_token == first_token)
                .group_by(self.table_def.columns.third_token)
            )
        else:
            sel_stmt = select(self.table_def.columns.third_token, self.table_def.columns.occurrences).where(
                and_(
                    self.table_def.columns.first_token == first_token,
                    self.table_def.columns.second_token == second_token,
                )
            )
        rows = engine.execute(sel_stmt).fetchall()
        chosen_token = self._choose_word_from_rows(rows)
        # In the event there is no link for the next choice, choose a new random one
        if not chosen_token:
            if not second_token:
                return self.get_first_token(engine)
            else:
                return self.get_next_token(engine, second_token)
        return chosen_token

    def detokenize(self, tokens: list[str]) -> str:
        """Detokenize a sequence of tokens using a nltk `TreebankWordDetokenizer`.

        Parameters
        ----------
        tokens : list[str]
            list of tokens to detokenize

        Returns
        -------
        str
            tokens reconstructed into sentences
        """
        return TreebankWordDetokenizer().detokenize(tokens).replace(" .", ".")


def train(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(description="Train a text generation Markov model.")
    parser.add_argument(
        "db_name",
        type=str,
        help="name of database to write model to",
    )
    parser.add_argument(
        "text_files",
        metavar="txt_file",
        nargs="+",
        type=str,
        help="text file to train from",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite occurrence counts when training instead of adding to existing counts",
    )
    parser.add_argument(
        "-r",
        "--remove-uncommon",
        type=int,
        default=0,
        help="delete records that have number of occurrences at or below the specified threshold",
    )
    args = parser.parse_args(argv)

    db_path = Directories.MODELS_DIR / f"{args.db_name}.db"
    # Decompress gzip-compressed db first if the db file doesn't exist
    if not os.path.exists(db_path) and os.path.exists(f"{db_path}.gz"):
        with gzip.open(f"{db_path}.gz", "rb") as f_src, open(db_path, "wb") as f_dst:
            f_dst.writelines(f_src)
    engine = create_engine(f"sqlite:///{db_path}", echo=True)
    markov_model = MarkovTriads()
    markov_model.create_table(engine)
    for fn in args.text_files:
        with open(fn) as f:
            markov_model.upsert_triads(engine, f.read(), overwrite_probs=args.overwrite)
    markov_model.remove_uncommon_tokens(engine, uncommon_threshold=args.remove_uncommon)
    # Remove deleted data
    engine.execute("vacuum")
    engine.dispose()
    # gzip-compress the db now
    with open(db_path, "rb") as f_src, gzip.open(f"{db_path}.gz", "wb") as f_dst:
        f_dst.writelines(f_src)
    os.remove(db_path)
