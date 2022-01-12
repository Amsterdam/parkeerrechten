from datetime import timedelta

import settings
from database import LocalDatabase
from object_store import ObjectStore


class Exporter:
    def __init__(self):
        super().__init__()
        self.local_db = LocalDatabase()
        self.object_store = ObjectStore()

    def export_orphans(self):
        batch_names = [settings.NPR_NULL_VALUE]
        self._run_export(batch_names)

    def export_range(self, start_date, end_date):
        batch_names = self.get_batch_names_for_export(start_date, end_date)
        self._run_export(batch_names)

    def _run_export(self, batch_names):
        for batch_name in batch_names:
            filename = f"{batch_name}_NPR_BACKUP.csv"
            self.local_db.export_batch_to_csv(filename, batch_name)

    def get_batch_names_for_export(self, start_date, end_date):
        num_days = (end_date - start_date).days + 1
        batch_names = [
            (start_date + timedelta(days=days)).strftime("%Y%m%d")
            for days in range(num_days)
        ]
        return batch_names
