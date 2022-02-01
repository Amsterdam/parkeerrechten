import os
from datetime import datetime, timedelta
from os.path import exists
from unittest import mock

import pytest

import settings
from exporter import Exporter
from models import NPRTable

BATCHES_IN_TEST_FILE = {
    '20170801',
    '20170802',
    '20170803',
    '20170804',
    '20170805',
    '20170806',
    '20170807',
    '20170808',
    '20170809',
    '20170810',
    '20170811',
    '20170812',
    '20170813',
    '20170814',
    '20170815',
    '20170816',
    '20170817',
    '20170818',
    '20170819',
    '20170821',
    '20170822',
    '20170823',
    '20170824',
    '20170825',
}


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
    @mock.patch('exporter.ObjectStore.upload')
    def test_export_range(
        self,
        mocked_upload,
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
        batch_names = {
            (start_date + timedelta(days=x)).strftime("%Y%m%d") for x in range(num_days)
        }
        batch_names = list(batch_names.intersection(BATCHES_IN_TEST_FILE))

        total_lines = 0

        for batch_name in batch_names:
            filename = f"{batch_name}_NPR_BACKUP.csv"
            path = os.path.join(settings.TMP_DATA_DIR, filename)
            mocked_upload.assert_any_call(path, filename)

            assert exists(path)
            with open(path) as f:
                lines = f.readlines()
                total_lines += len(lines) - 1  # don't count the header

                # cleanup
                os.remove(path)

        assert total_lines == total_expected_lines

    @mock.patch('exporter.ObjectStore.upload')
    def test_export_orphans(self, mocked_upload, local_db, import_test_data):
        with local_db.session() as session:
            num = session.query(NPRTable).count()
            assert num > 0

        exporter = Exporter()
        exporter.export_orphans()

        filename = "Leeg_NPR_BACKUP.csv"
        path = os.path.join(settings.TMP_DATA_DIR, filename)
        mocked_upload.assert_called_with(path, filename)
        with open(path) as f:
            lines = f.readlines()
            assert len(lines) == 17

            # cleanup
            os.remove(path)
