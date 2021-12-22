import os
from datetime import datetime, timedelta

import pytest

import settings
from exporter import Exporter
from models import NPRTable


class TestExporter:
    @pytest.mark.parametrize(
        "start_date_str,num_days,num_expected",
        [
            ("20170731", 1, 0),  # first day is 01/08 so no import
            ("20170801", 0, 0),  # 0 if num days is zero
            ("20170801", 1, 8),  # 8 on first day
            ("20170825", 1, 2),  # 2 on last day
            ("20170826", 1, 0),  # last day is 25/08 so no import
            ("20170731", 365, 84),  # 84 in time window
        ],
    )
    def test_export_range(self, local_db, start_date_str, num_days, num_expected):
        exporter = Exporter()
        start_date = datetime.strptime(start_date_str, "%Y%m%d")
        exporter.export_range(start_date, num_days)

        batch_names = [
            (start_date + timedelta(days=x)).strftime("%Y%m%d") for x in range(num_days)
        ]
        for batch_name in batch_names:
            filename = f"{batch_name}_NPR_BACKUP.csv"
            path = os.path.join(settings.TMP_DATA_DIR, filename)
            with open(path) as f:
                lines = f.readlines()
                assert len(lines) > 0

    def test_export_orphans(self, local_db, import_test_data):
        with local_db.session() as session:
            num = session.query(NPRTable).count()
            assert num > 0

        exporter = Exporter()
        exporter.export_orphans()

        filename = "Leeg_NPR_BACKUP.csv"
        path = os.path.join(settings.TMP_DATA_DIR, filename)
        with open(path) as f:
            lines = f.readlines()
            assert len(lines) == 17
