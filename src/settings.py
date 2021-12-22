import os

from sqlalchemy.engine import URL

NPR_DB_URL = URL(
    drivername=os.getenv('NPR_DB_DRIVER', 'mssql+pymssql'),
    username=os.environ['NPR_DB_USER'],
    password=os.environ['NPR_DB_PASSWORD'],
    host=os.environ['NPR_DB_HOST'],
    port=os.environ['NPR_DB_PORT'],
    database=os.environ['NPR_DB_NAME'],
)

NPR_DB_TABLE_NAME = os.environ['NPR_DB_TABLE_NAME']

NPR_NULL_VALUE = 'Leeg'

LOCAL_DB_URL = URL(
    drivername=os.getenv('LOCAL_DB_DRIVER', 'postgresql+psycopg2'),
    username=os.getenv('LOCAL_DB_USER', 'dev'),
    password=os.getenv('LOCAL_DB_PASSWORD', 'dev'),
    host=os.getenv('LOCAL_DB_HOST', 'database'),
    port=os.getenv('LOCAL_DB_PORT', '5432'),
    database=os.getenv('LOCAL_DB_NAME', 'dev'),
)

BATCH_SIZE = os.getenv('BATCH_SIZE', 50000)

TMP_DATA_DIR = os.getenv('TMP_DATA_DIR', '/data')
