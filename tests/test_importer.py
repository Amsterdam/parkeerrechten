from datetime import datetime

import pytest

from importer import Importer
from models import NPRTable


class TestImporter:
    @pytest.mark.parametrize(
        "start_date_str,num_days,num_expected",
        [
            ("20170731", 1, 0),     # first day is 01/08 so no import
            ("20170801", 0, 0),     # 0 if num days is zero
            ("20170801", 1, 8),     # 8 on first day
            ("20170825", 1, 2),     # 2 on last day
            ("20170826", 1, 0),     # last day is 25/08 so no import
            ("20170731", 365, 84),    # 84 in time window
        ],
    )
    def test_import_range(self, local_db, start_date_str, num_days, num_expected):
        importer = Importer()
        start_date = datetime.strptime(start_date_str, "%Y%m%d")
        importer.import_range(start_date, num_days)

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
