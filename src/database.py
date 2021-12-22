import logging
import os
import sys
import time

from sqlalchemy import MetaData, Table, distinct, asc, literal, insert
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.future import create_engine, select
from sqlalchemy.orm import sessionmaker

import settings
from models import Base, NPRTable
from util import validate_batch_names


class Database:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    engine = None
    sessionmaker = None

    def __init__(self):
        super().__init__()
        self.engine = create_engine(self.get_connection_url(), future=True)
        self.sessionmaker = sessionmaker(self.engine)

    def get_connection_url(self):
        raise NotImplementedError()

    def get_table_name(self):
        raise NotImplementedError()

    def get_num_rows(self):
        with self.session() as session:
            num = session.query(NPRTable).count()
        return num

    def session(self):
        # call begin() so when leaving the context the transaction is committed
        return self.sessionmaker.begin()

    def get_introspected_table(self):
        return Table(self.get_table_name(), MetaData(), autoload_with=self.engine)

    def get_existing_batch_names(self, include_empty=False, require_table=True):
        """
        Query for all distinct batchnames in database (be it NPR, local or test).
        """
        # Introspect the database for table definition, define selection.
        try:
            view = self.get_introspected_table()
        except NoSuchTableError:
            if require_table:
                raise
            else:
                return []

        selection = select(distinct(view.c.VER_BATCH_NAAM)).order_by(
            asc(view.c.VER_BATCH_NAAM)
        )

        # We expect maximum on the order of a few hundred days (for the NPR
        # database, the local database used during testing and importing
        # should have only on the order of tens of batches).
        with self.session() as session:
            unvalidated_batchnames = [
                row[0] for row in session.execute(selection).fetchall()
            ]

        # Validate that we have only dates as batch names.
        batch_names = validate_batch_names(
            unvalidated_batchnames, include_empty=include_empty
        )

        return batch_names


class NPRDatabase(Database):
    NULL_VALUE = 'Leeg'

    def get_connection_url(self):
        return settings.NPR_DB_URL

    def get_table_name(self):
        return settings.NPR_DB_TABLE_NAME

    def get_backup_selection(self, batch_name):
        table = self.get_introspected_table()
        selection = (
            select(table)
            .where(table.c.VER_BATCH_NAAM == literal(batch_name))
            .order_by(asc(table.c.VERW_RECHT_ID))
        )
        return selection

    def get_backup_iterator(self, batch_name, batch_size):
        """
        Given an SQLAlchemy connection + selection query, provide batched iterator.
        """
        selection = self.get_backup_selection(batch_name)
        offset = 0
        with self.session() as session:
            while True:
                start = time.perf_counter()
                selection = selection.limit(batch_size).offset(offset)
                rows = session.execute(selection).mappings().all()
                end = time.perf_counter()
                num_rows = len(rows)
                self.logger.info(f"> Getting {num_rows} rows took {end - start:.2f}s")

                offset += batch_size

                # For quick test runs.
                if not rows:
                    break

                yield rows

                # prevent unnecessary extra (slow) query
                if num_rows < batch_size:
                    break


class LocalDatabase(Database):

    def __init__(self):
        super().__init__()

        # create tables if they dont exist
        Base.metadata.create_all(self.engine, checkfirst=True)

    def get_connection_url(self):
        return settings.LOCAL_DB_URL

    def get_table_name(self):
        return settings.NPR_DB_TABLE_NAME

    def backup_iterator(self, iterator):
        with self.session() as session:
            for rows in iterator:
                start = time.perf_counter()
                session.execute(insert(NPRTable.__table__), rows)
                end = time.perf_counter()
                self.logger.info(f"> Inserting {len(rows)} rows took {end - start:.2f}s")

    def export_batch_to_csv(self, output_filename, batch_name):
        output_path = self.ensure_path(output_filename)

        sql = f"""
            COPY (
                SELECT * 
                FROM "{self.get_table_name()}" 
                WHERE "VER_BATCH_NAAM"='{batch_name}'
            ) TO STDOUT WITH CSV HEADER;
        """

        # Warning: "copy_expert" is a psycopg2 stored procedure and can only be
        # used with postgres, therefore we use a raw connection
        conn = self.engine.raw_connection()
        try:
            cursor = conn.cursor()
            with open(output_path, "w") as f:
                cursor.copy_expert(sql, f)

            cursor.close()
            conn.commit()
        finally:
            conn.close()

        return output_path

    def ensure_path(self, filename):
        full_path = os.path.abspath(os.path.join(settings.TMP_DATA_DIR, filename))
        dirname = os.path.dirname(full_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        return full_path
