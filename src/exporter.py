import datetime
import logging
import sys
from datetime import timedelta

import settings
from database import LocalDatabase
from object_store import ObjectStore

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class Exporter:
    def __init__(self):
        super().__init__()
        self.local_db = LocalDatabase()
        self.object_store = ObjectStore()

    def export_orphans(self):
        batch_names = [settings.NPR_NULL_VALUE]
        self._run_export(batch_names)

    def export_range(self, start_date, end_date):
        today = datetime.date.today()
        if end_date >= today:
            # ensure we never export today as its data is still incomplete
            end_date = today - datetime.timedelta(days=1)

        batch_names = self.get_batch_names_for_export(start_date, end_date)

        logger.info(f"Found {len(batch_names)} batch names for export")
        self._run_export(batch_names)

    def _run_export(self, batch_names):
        for batch_name in batch_names:
            filename = f"{batch_name}{settings.BACKUP_FILE_POSTFIX}"
            try:
                path = self.local_db.export_batch_to_csv(filename, batch_name)
                self.object_store.upload(path, filename)
                logger.info(f"Exported batch {batch_name}")
            except:
                logger.exception(f"Failed to export batch to csv {batch_name}")

    def get_batch_names_for_export(self, start_date, end_date):
        num_days = (end_date - start_date).days + 1
        batch_names = [
            (start_date + timedelta(days=days)).strftime("%Y%m%d")
            for days in range(num_days)
        ]

        existing_batch_names = self.local_db.get_existing_batch_names()
        batches = set(batch_names).intersection(set(existing_batch_names))
        return sorted(list(batches))
