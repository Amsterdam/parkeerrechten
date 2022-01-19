import csv
import os
from datetime import date

import pytest

from database import NPRDatabase, LocalDatabase
from importer import Importer
from models import NPRTable, Base

TEST_CSV_FILENAME = os.path.join(os.path.dirname(__name__), 'test-data.csv')


def _get_test_data():
    with open(TEST_CSV_FILENAME, 'r') as f:
        reader = csv.DictReader(f, delimiter=',')
        rows = [r for r in reader]

    return rows


def _init_database(dbclass):
    db = dbclass()
    Base.metadata.drop_all(bind=db.engine, checkfirst=True)
    Base.metadata.create_all(bind=db.engine, checkfirst=True)
    assert db.get_num_rows() == 0
    return db


@pytest.fixture(autouse=True, scope="session")
def npr_db():
    """
    Load test data from provided CSV.
    """
    npr_db = _init_database(NPRDatabase)

    # insert data
    with npr_db.session() as session:
        test_data_rows = _get_test_data()
        session.bulk_insert_mappings(NPRTable, test_data_rows)

    return npr_db


@pytest.fixture(autouse=True, scope="function")
def local_db():
    return _init_database(LocalDatabase)


@pytest.fixture
def import_test_data(local_db):
    importer = Importer()
    start_date = date(year=2017, month=1, day=1)
    end_date = date(year=2018, month=1, day=1)
    importer.import_range(start_date, end_date, override_existing=True)
    importer.import_orphans()
    assert local_db.get_num_rows() == 100
