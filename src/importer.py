import datetime
import logging
import sys
import time

import settings
from database import LocalDatabase, NPRDatabase
from object_store import ObjectStore
from util import filter_batch_names

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class Importer:
    def __init__(self):
        super().__init__()
        self.local_db = LocalDatabase()
        self.npr_db = NPRDatabase()
        self.object_store = ObjectStore()

    def import_orphans(self):
        batch_names = [settings.NPR_NULL_VALUE]
        self._run_import(batch_names)

    def import_range(self, start_date, end_date, override_existing=False):
        today = datetime.date.today()
        if end_date >= today:
            # ensure we never import today as its data is still incomplete
            end_date = today - datetime.timedelta(days=1)

        logger.info("Determining batch names for import...")
        batch_names = self.get_batch_names_for_download(
            start_date, end_date, override_existing
        )
        logger.info(f"{len(batch_names)} batches found to import")
        self._run_import(batch_names)

    def import_last_x_days(self, num_days):
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=num_days)
        return self.import_range(start_date, today)

    def _run_import(self, batch_names):
        if not batch_names:
            logger.info("Nothing to import")
            return

        for batch_name in batch_names:
            self.backup_batch(batch_name)

    def get_batch_names_for_download(self, start_date, end_date, override_existing):
        # We want batches that are requested and not yet backed up
        # (these are the set of candidates to back up).

        if override_existing:
            backed_up = []
        else:
            batch_names_in_local_db = self.local_db.get_existing_batch_names(
                require_table=False
            )
            batch_names_in_obj_store = self.object_store.get_existing_batch_names()
            backed_up = batch_names_in_obj_store + batch_names_in_local_db

        batch_names = self.npr_db.get_existing_batch_names()
        batch_names = filter_batch_names(start_date, end_date, batch_names)

        batch_names = list(set(batch_names) - set(backed_up))
        batch_names.sort()
        return batch_names

    def backup_batch(self, batch_name):
        """
        Retrieve records from NPR, store them in local database in batches.
        """
        logger.info(f"Backing up batch {batch_name}. Getting iterator...")
        npr_backup_iterator = self.npr_db.get_backup_iterator(
            batch_name, batch_size=settings.BATCH_SIZE
        )

        logger.info("Starting local import")
        start = time.perf_counter()
        self.local_db.backup_iterator(npr_backup_iterator)
        end = time.perf_counter()
        logger.info(f">> Done. Processing iterator took {end - start:0.2f}s")
