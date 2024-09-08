from dataclasses import dataclass, field
from sqlalchemy import Table, MetaData, Column, select, delete
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.engine import Engine
from sqlalchemy.schema import DropTable
from typing import Iterator, Literal


def batch_list(records: list[dict], batch_size: int = 100) -> Iterator[list[dict]]:
    """Chunk a dataframe into smaller batches.

    Parameters
    ----------
    records : list[dict]
        list of records to chunk into batches
    batch_size : int, optional
        size of each batch, by default 100

    Yields
    ------
    Iterator[list[dict]]
        iterator of batches of records
    """
    for i in range(0, len(records), batch_size):
        yield records[i : i + batch_size]


@dataclass
class UpsertTable:
    """Represents a table with the ability to upsert values."""

    table_name: str
    columns: list[Column]
    metadata: MetaData = field(default_factory=MetaData)
    table_def: Table = field(init=False)

    def __post_init__(self) -> None:
        self.table_def = Table(self.table_name, self.metadata, *self.columns)

    def create_table(self, engine: Engine) -> None:
        """Create this table with the specified engine.

        Parameters
        ----------
        engine : Engine
            SQLAlchemy engine to create the table in
        """
        self.metadata.create_all(engine)

    def upsert(self, engine: Engine, records: list[dict], upsert_type: Literal["overwrite", "add"] = "overwrite") -> None:
        """Upsert the dataframe into this table with the specified engine.

        Note that the dataframe must have all the PK columns of this table, or it will raise a `ValueError`.

        Parameters
        ----------
        engine : Engine
            SQLAlchemy engine to create the table in
        records : list[dict]
            list of records to upsert; must have all PK columns of this table
        upsert_type : Literal["overwrite", "add"]
            "overwrite" if upserted values should be overwritten; "add" if upserted values should be added to existing values

        Raises
        ------
        ValueError
            If any of the following occur:
            - Input dataframe has one or more columns not matching the table schema
            - Input dataframe doesn't have all the PK columns of this table
            - Input dataframe has no value columns to upsert with
        """
        UPSERT_CHUNK_SIZE = 50000
        table_pk_names = [col.name for col in self.columns if col.primary_key]
        table_upd_names = [col.name for col in self.columns if not col.primary_key]
        # Check that each record has the required columns
        for record in records:
            for field in table_pk_names:
                if field not in record:
                    raise ValueError(f"Input record {record} does not have PK column {field}")
            for field in table_upd_names:
                if field not in record:
                    raise ValueError(f"Input record {record} does not have value column {field}")

        # Create temp table and load data into it
        temp_table_name = f"load_{self.table_name}"
        temp_metadata = MetaData()
        temp_table = self.table_def.to_metadata(temp_metadata, name=temp_table_name)
        temp_metadata.create_all(engine)

        for batch in batch_list(records, batch_size=UPSERT_CHUNK_SIZE):
            # Do all as a single transaction
            with engine.begin() as conn:
                # Overwrite the table between chunks
                conn.execute(delete(temp_table))
                conn.execute(insert(temp_table), batch)

                # Then do upsert from this table, dependent on upsert type chosen
                ins_stmt = insert(self.table_def).from_select(table_pk_names + table_upd_names, select(temp_table).where(True))
                if upsert_type == "overwrite":
                    set_map = {col: ins_stmt.excluded[col] for col in table_upd_names}
                else:
                    set_map = {col: Column(col) + ins_stmt.excluded[col] for col in table_upd_names}
                upd_stmt = ins_stmt.on_conflict_do_update(index_elements=table_pk_names, set_=set_map)

                conn.execute(upd_stmt)

        engine.execute(DropTable(temp_table, if_exists=True))
