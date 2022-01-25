import os
from datetime import datetime, timedelta
from os.path import exists

import pytest

import settings
from exporter import Exporter
from models import NPRTable


class TestExporter:
    @pytest.mark.parametrize(
        "start_date_str,end_date_str,num_expected_files,total_expected_lines",
        [
            ("20170731", "20170731", 0, 0),  # first day is 01/08 so no import
            ("20170801", "20170801", 1, 8),  # 8 on first day
            ("20170825", "20170825", 1, 2),  # 2 on last day
            ("20170826", "20170826", 0, 0),  # last day is 25/08 so no import
            ("20170731", "20170826", 24, 84),  # 84 in time window
        ],
    )
    def test_export_range(
        self,
        import_test_data,
        start_date_str,
        end_date_str,
        num_expected_files,
        total_expected_lines,
    ):
        exporter = Exporter()
        start_date = datetime.strptime(start_date_str, "%Y%m%d").date()
        end_date = datetime.strptime(end_date_str, "%Y%m%d").date()
        exporter.export_range(start_date, end_date)

        num_days = (end_date - start_date).days + 1
        batch_names = [
            (start_date + timedelta(days=x)).strftime("%Y%m%d") for x in range(num_days)
        ]

        num_files = 0
        total_lines = 0

        for batch_name in batch_names:
            filename = f"{batch_name}_NPR_BACKUP.csv"
            path = os.path.join(settings.TMP_DATA_DIR, filename)
            if exists(path):
                num_files += 1
                with open(path) as f:
                    lines = f.readlines()
                    total_lines += len(lines) - 1  # don't count the header

                # cleanup
                os.remove(path)

        assert num_files == num_expected_files
        assert total_lines == total_expected_lines

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

            # cleanup
            os.remove(path)
