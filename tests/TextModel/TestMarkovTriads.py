import unittest
from unittest.mock import patch
from sqlalchemy import create_engine, select
from sqlalchemy.engine import Row
from typing import Optional

from src.TextModel.MarkovTriads import MarkovTriads


class TestMarkovTriads(unittest.TestCase):
    """Tests for Markov triads."""

    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        self.first_sample_text = "This is a unit test. Writing a unit test."
        self.second_sample_text = "This is another unit test."

    def _choose_word_from_rows_deterministic(self, rows: list[Row]) -> Optional[str]:
        """Choose a word from the given rows in a deterministic way, always getting the earliest word in the alphabet."""
        if len(rows) == 0:
            return None
        words = sorted((row[0] for row in rows), key=lambda row: row[0].lower())
        return words[0]

    def test_upsert_triads(self) -> None:
        """Test upserting Markov triads into the database from input text."""
        markov_model = MarkovTriads()
        markov_model.create_table(self.engine)

        # Test initial insert
        markov_model.upsert_triads(self.engine, self.first_sample_text, overwrite_probs=False)
        expected = [
            {"first_token": ".", "second_token": "This", "third_token": "is", "occurrences": 1},
            {"first_token": ".", "second_token": "Writing", "third_token": "a", "occurrences": 1},
            {"first_token": "This", "second_token": "is", "third_token": "a", "occurrences": 1},
            {"first_token": "Writing", "second_token": "a", "third_token": "unit", "occurrences": 1},
            {"first_token": "a", "second_token": "unit", "third_token": "test", "occurrences": 2},
            {"first_token": "is", "second_token": "a", "third_token": "unit", "occurrences": 1},
            {"first_token": "test", "second_token": ".", "third_token": "This", "occurrences": 1},
            {"first_token": "test", "second_token": ".", "third_token": "Writing", "occurrences": 1},
            {"first_token": "unit", "second_token": "test", "third_token": ".", "occurrences": 2},
        ]
        with self.engine.connect() as conn:
            result = conn.execute(select([markov_model.table_def]).order_by("first_token", "second_token", "third_token"))
            self.assertEqual(result.mappings().all(), expected)

        # Test upsert with adding to values
        markov_model.upsert_triads(self.engine, self.second_sample_text, overwrite_probs=False)
        expected = [
            {"first_token": ".", "second_token": "This", "third_token": "is", "occurrences": 2},
            {"first_token": ".", "second_token": "Writing", "third_token": "a", "occurrences": 1},
            {"first_token": "This", "second_token": "is", "third_token": "a", "occurrences": 1},
            {"first_token": "This", "second_token": "is", "third_token": "another", "occurrences": 1},
            {"first_token": "Writing", "second_token": "a", "third_token": "unit", "occurrences": 1},
            {"first_token": "a", "second_token": "unit", "third_token": "test", "occurrences": 2},
            {"first_token": "another", "second_token": "unit", "third_token": "test", "occurrences": 1},
            {"first_token": "is", "second_token": "a", "third_token": "unit", "occurrences": 1},
            {"first_token": "is", "second_token": "another", "third_token": "unit", "occurrences": 1},
            {"first_token": "test", "second_token": ".", "third_token": "This", "occurrences": 2},
            {"first_token": "test", "second_token": ".", "third_token": "Writing", "occurrences": 1},
            {"first_token": "unit", "second_token": "test", "third_token": ".", "occurrences": 3},
        ]
        with self.engine.connect() as conn:
            result = conn.execute(select([markov_model.table_def]).order_by("first_token", "second_token", "third_token"))
            self.assertEqual(result.mappings().all(), expected)

        # Test upsert overwriting values
        markov_model.upsert_triads(self.engine, self.second_sample_text, overwrite_probs=True)
        expected = [
            {"first_token": ".", "second_token": "This", "third_token": "is", "occurrences": 1},
            {"first_token": ".", "second_token": "Writing", "third_token": "a", "occurrences": 1},
            {"first_token": "This", "second_token": "is", "third_token": "a", "occurrences": 1},
            {"first_token": "This", "second_token": "is", "third_token": "another", "occurrences": 1},
            {"first_token": "Writing", "second_token": "a", "third_token": "unit", "occurrences": 1},
            {"first_token": "a", "second_token": "unit", "third_token": "test", "occurrences": 2},
            {"first_token": "another", "second_token": "unit", "third_token": "test", "occurrences": 1},
            {"first_token": "is", "second_token": "a", "third_token": "unit", "occurrences": 1},
            {"first_token": "is", "second_token": "another", "third_token": "unit", "occurrences": 1},
            {"first_token": "test", "second_token": ".", "third_token": "This", "occurrences": 1},
            {"first_token": "test", "second_token": ".", "third_token": "Writing", "occurrences": 1},
            {"first_token": "unit", "second_token": "test", "third_token": ".", "occurrences": 1},
        ]
        with self.engine.connect() as conn:
            result = conn.execute(select([markov_model.table_def]).order_by("first_token", "second_token", "third_token"))
            self.assertEqual(result.mappings().all(), expected)

    def test_remove_uncommon_tokens(self) -> None:
        """Test removing uncommon tokens from the database."""
        markov_model = MarkovTriads()
        markov_model.create_table(self.engine)
        markov_model.upsert_triads(self.engine, self.first_sample_text)
        markov_model.remove_uncommon_tokens(self.engine, uncommon_threshold=1)
        expected = [
            {"first_token": ".", "second_token": "This", "third_token": "is", "occurrences": 1},
            {"first_token": ".", "second_token": "Writing", "third_token": "a", "occurrences": 1},
            {"first_token": "test", "second_token": ".", "third_token": "This", "occurrences": 1},
            {"first_token": "test", "second_token": ".", "third_token": "Writing", "occurrences": 1},
        ]
        with self.engine.connect() as conn:
            result = conn.execute(select([markov_model.table_def]).order_by("first_token", "second_token", "third_token"))
            self.assertEqual(result.mappings().all(), expected)

    def test_get_first_token(self) -> None:
        """Test getting the first token for a generated sentence."""
        markov_model = MarkovTriads()
        markov_model.create_table(self.engine)
        markov_model.upsert_triads(self.engine, self.first_sample_text)
        with patch.object(markov_model, "_choose_word_from_rows", self._choose_word_from_rows_deterministic):
            first_token = markov_model.get_first_token(self.engine)
            self.assertEqual(first_token, "This")

    def test_get_next_token(self) -> None:
        """Test getting the next token for a generated sentence."""
        markov_model = MarkovTriads()
        markov_model.create_table(self.engine)
        markov_model.upsert_triads(self.engine, self.first_sample_text)
        with patch.object(markov_model, "_choose_word_from_rows", self._choose_word_from_rows_deterministic):
            next_token = markov_model.get_next_token(self.engine, first_token="is")
            self.assertEqual(next_token, "a")

            next_token = markov_model.get_next_token(self.engine, first_token="test", second_token=".")
            self.assertEqual(next_token, "This")
