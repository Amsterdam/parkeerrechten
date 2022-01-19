import logging

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

    def get_existing_batch_names(self):
        """
        Get list of existing batches in the object store.
        """
        connection = self.get_connection()
        documents_meta = objectstore.get_full_container_list(
            connection, settings.OBJECTSTORE_CONTAINER_NAME
        )
        batch_names = [
            meta.get('name').replace(settings.BACKUP_FILE_POSTFIX, "")
            for meta in documents_meta
            if meta.get('content_type') != DIR_CONTENT_TYPE
        ]
        return batch_names

    def upload(self, filepath, filename):
        try:
            file = open(filepath, "rb")
            connection = self.get_connection()
            logger.info(f"Uploading {filename}...")
            connection.put_object(
                container=settings.OBJECTSTORE_CONTAINER_NAME,
                obj=filename,
                contents=file,
                content_type="text/csv"
            )
        except:
            logger.exception(f"Failed to upload batch {filename}")
