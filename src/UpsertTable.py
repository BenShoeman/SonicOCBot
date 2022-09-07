from dataclasses import dataclass, field
import pandas as pd
from sqlalchemy import Table, MetaData, Column, select, delete
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.engine import Engine
from sqlalchemy.schema import DropTable
from typing import Iterator, Literal


def batch_df(df: pd.DataFrame, batch_size: int = 100) -> Iterator[pd.DataFrame]:
    """Chunk a dataframe into smaller batches.

    Parameters
    ----------
    df : pd.DataFrame
        Pandas dataframe to chunk into batches
    batch_size : int, optional
        size of each batch, by default 100

    Yields
    ------
    Iterator[pd.DataFrame]
        iterator of dataframe batches
    """
    for i in range(0, len(df), batch_size):
        yield df.iloc[i : i + batch_size]


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

    def upsert(self, engine: Engine, df: pd.DataFrame, upsert_type: Literal["overwrite", "add"] = "overwrite") -> None:
        """Upsert the dataframe into this table with the specified engine.

        Note that the dataframe must have all the PK columns of this table, or it will raise a `ValueError`.

        Parameters
        ----------
        engine : Engine
            SQLAlchemy engine to create the table in
        df : pd.DataFrame
            Pandas dataframe to upsert; must have all PK columns of this table
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
        table_col_names = [col.name for col in self.columns]
        table_pk_names = [col.name for col in self.columns if col.primary_key]
        table_upd_names = [name for name in df.columns if name not in table_pk_names]
        if not all(df_col in table_col_names for df_col in df.columns):
            raise ValueError(f"Dataframe with columns {df.columns} has one or more columns that don't match this schema")
        elif not all(pk_col in df.columns for pk_col in table_pk_names):
            raise ValueError(f"Dataframe with columns {df.columns} doesn't contain all PK columns {table_pk_names}")
        elif len(table_upd_names) == 0:
            raise ValueError(f"Dataframe with columns {df.columns} has no value columns to upsert with")

        # Create temp table and load pandas data into it
        temp_table_name = f"load_{self.table_name}"
        temp_metadata = MetaData()
        temp_table = self.table_def.to_metadata(temp_metadata, name=temp_table_name)
        temp_metadata.create_all(engine)

        for microdf in batch_df(df, batch_size=UPSERT_CHUNK_SIZE):
            # Do all as a single transaction
            with engine.connect() as conn:
                # Wipe the table between chunks
                conn.execute(delete(temp_table))

                microdf.to_sql(temp_table_name, conn, index=False, if_exists="append", method="multi")

                # Then do upsert from this table, dependent on upsert type chosen
                ins_stmt = insert(self.table_def).from_select(table_pk_names + table_upd_names, select(temp_table).where(True))
                if upsert_type == "overwrite":
                    set_map = {col: ins_stmt.excluded[col] for col in table_upd_names}
                else:
                    set_map = {col: Column(col) + ins_stmt.excluded[col] for col in table_upd_names}
                upd_stmt = ins_stmt.on_conflict_do_update(index_elements=table_pk_names, set_=set_map)

                conn.execute(upd_stmt)

        engine.execute(DropTable(temp_table, if_exists=True))
