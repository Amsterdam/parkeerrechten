from datetime import datetime, timedelta

import settings
from exporter import Exporter
from importer import Importer

if __name__ == "__main__":
    """
    Import the last 7 days of data from the RDW database
    and export the data in CSV files to the objectstore. 
    """
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=settings.NUM_DAYS_TO_IMPORT)

    importer = Importer()
    importer.import_range(start_date, end_date)

    exporter = Exporter()
    exporter.export_range(start_date, end_date)

