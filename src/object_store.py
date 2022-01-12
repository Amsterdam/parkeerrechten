from objectstore import objectstore

import settings

DIR_CONTENT_TYPE = 'application/directory'


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
        :param connection: swiftclient connection
        :return: Array of documents in the form:
        [('rapportage', 'QE1_rapportage_Some_where - some extra info.pdf'), ... ]
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
