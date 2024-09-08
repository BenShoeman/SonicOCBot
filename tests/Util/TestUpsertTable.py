import unittest
from sqlalchemy import Column, Integer, create_engine, select, inspect

from src.UpsertTable import UpsertTable


class TestUpsertTable(unittest.TestCase):
    """Tests for the UpsertTable class."""

    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")

    def test_create_table(self) -> None:
        """Test creating a table."""
        test_table = UpsertTable("test", [Column("id", Integer, primary_key=True), Column("value", Integer)])
        test_table.create_table(self.engine)
        inspector = inspect(self.engine)
        self.assertTrue(inspector.has_table("test"))

    def test_upsert(self) -> None:
        """Test upserting into a table with the upsert function."""
        test_table = UpsertTable("test", [Column("id", Integer, primary_key=True), Column("value", Integer)])
        test_table.create_table(self.engine)

        records = [{"id": 1, "value": 2}, {"id": 3, "value": 4}]
        test_table.upsert(self.engine, records)
        with self.engine.connect() as conn:
            result = conn.execute(select([test_table.table_def]))
            self.assertEqual(result.mappings().all(), [{"id": 1, "value": 2}, {"id": 3, "value": 4}])

        records = [{"id": 3, "value": 6}]
        test_table.upsert(self.engine, records)
        with self.engine.connect() as conn:
            result = conn.execute(select([test_table.table_def]))
            self.assertEqual(result.mappings().all(), [{"id": 1, "value": 2}, {"id": 3, "value": 6}])

    def test_upsert_valueerror(self) -> None:
        """Test upserting with ValueError in the upsert function."""
        test_table = UpsertTable("test", [Column("id", Integer, primary_key=True), Column("value", Integer)])
        test_table.create_table(self.engine)

        records = [{"id": 1}, {"id": 3, "value": 4}]
        error_message = "Input record {'id': 1} does not have value column 'value'"
        with self.assertRaises(ValueError, msg=error_message):
            test_table.upsert(self.engine, records)

        records = [{"id": 1, "value": 2}, {"value": 3}]
        error_message = "Input record {'value': 3} does not have PK column 'id'"
        with self.assertRaises(ValueError, msg=error_message):
            test_table.upsert(self.engine, records)
