import logging
import os

from objectstore import objectstore

import settings

DIR_CONTENT_TYPE = 'application/directory'

logger = logging.getLogger(__name__)


class ObjectStore:
    def __init__(self, config=settings.OBJECTSTORE_CONNECTION_CONFIG):
        self.connection = None
        self.config = config
        super().__init__()

    def get_connection(self):
        if not self.connection:
            self.connection = objectstore.get_connection(self.config)
        return self.connection

    def get_existing_batch_names(self, include_processed=True):
        """
        Get list of existing batches in the object store.
        """
        folders = [settings.OBJECTSTORE_CONTAINER_NAME]
        if include_processed and settings.OBJECTSTORE_PROCESSED_FOLDER_NAME:
            folders.append(
                os.path.join(
                    settings.OBJECTSTORE_CONTAINER_NAME,
                    settings.OBJECTSTORE_PROCESSED_FOLDER_NAME,
                )
            )

        connection = self.get_connection()
        batch_names = []

        for folder in folders:
            documents_meta = objectstore.get_full_container_list(connection, folder)
            for meta in documents_meta:
                if meta.get('content_type') != DIR_CONTENT_TYPE:
                    batch_names.append(
                        meta['name'].replace(settings.BACKUP_FILE_POSTFIX, "")
                    )

        # return sorted, unique list of existing batch names
        return sorted(list(set(batch_names)))

    def upload(self, filepath, filename):
        try:
            with open(filepath, "rb") as file:
                connection = self.get_connection()
                logger.info(f"Uploading {filename}...")
                connection.put_object(
                    container=settings.OBJECTSTORE_CONTAINER_NAME,
                    obj=filename,
                    contents=file,
                    content_type="text/csv",
                )
        except:
            logger.exception(f"Failed to upload batch {filename}")
