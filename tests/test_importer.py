from datetime import datetime
from unittest import mock

import pytest

from importer import Importer
from models import NPRTable


class TestImporter:
    @mock.patch('importer.ObjectStore')
    @pytest.mark.parametrize(
        "start_date_str,end_date_str,num_expected",
        [
            ("20170731", "20170731", 0),  # first day is 01/08 so no import
            ("20170801", "20170801", 8),  # 8 on first day
            ("20170825", "20170825", 2),  # 2 on last day
            ("20170826", "20170826", 0),  # last day is 25/08 so no import
            ("20170731", "20170826", 84),  # 84 in time window
        ],
    )
    def test_import_range(
        self, mocked_objectstore, local_db, start_date_str, end_date_str, num_expected
    ):
        mocked_objectstore.get_existing_batch_names = []

        importer = Importer()
        start_date = datetime.strptime(start_date_str, "%Y%m%d").date()
        end_date = datetime.strptime(end_date_str, "%Y%m%d").date()
        importer.import_range(start_date, end_date)

        with local_db.session() as session:
            num = session.query(NPRTable).count()
            assert num == num_expected

    def test_import_orphans(self, local_db):
        # assert that we import all 16 orphans (batch name = "Leeg") in de test csv
        importer = Importer()
        importer.import_orphans()

        with local_db.session() as session:
            num = session.query(NPRTable).count()
            assert num == 16
