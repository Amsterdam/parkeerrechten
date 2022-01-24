from unittest import mock

from object_store import ObjectStore


class TestObjectStore:
    def test_init(self):
        objectstore = ObjectStore(config='foobar')
        assert objectstore.config == 'foobar'
        assert objectstore.connection is None

    @mock.patch('object_store.objectstore')
    def test_get_connection(self, mocked_base_objstore):
        mocked_base_objstore.get_connection.return_value = 'conn'

        objectstore = ObjectStore(config='foobar')
        connection = objectstore.get_connection()
        assert connection == objectstore.connection
        assert connection == objectstore.get_connection()
