import os

import sentry_sdk
from sqlalchemy.engine import URL

from util import str_to_bool

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

BATCH_SIZE = int(os.getenv('BATCH_SIZE', 50000))

NUM_DAYS_TO_IMPORT = int(os.getenv('NUM_DAYS_TO_IMPORT', 14))
OVERRIDE_EXISTING = str_to_bool(os.getenv('OVERRIDE_EXISTING', 'false'))

TMP_DATA_DIR = os.getenv('TMP_DATA_DIR', '/data')

OBJECTSTORE_CONNECTION_CONFIG = dict(
    VERSION="2.0",
    AUTHURL="https://identity.stack.cloudvps.com/v2.0",
    TENANT_NAME=os.getenv("OBJECTSTORE_TENANT_NAME"),
    TENANT_ID=os.getenv("OBJECTSTORE_TENANT_ID"),
    USER=os.getenv("OBJECTSTORE_USER"),
    PASSWORD=os.getenv("OBJECTSTORE_PASSWORD"),
    REGION_NAME="NL",
)
OBJECTSTORE_CONTAINER_NAME = os.getenv("OBJECTSTORE_CONTAINER_NAME")
OBJECTSTORE_PROCESSED_FOLDER_NAME = os.getenv(
    "OBJECTSTORE_PROCESSED_FOLDER_NAME", "processed"
)

BACKUP_FILE_POSTFIX = "_NPR_BACKUP.csv"

SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN)
