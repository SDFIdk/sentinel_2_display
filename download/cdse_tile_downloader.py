import itertools

from cdsetool.query import query_features
from cdsetool.credentials import Credentials
from cdsetool.download import download_features
from cdsetool.monitor import StatusMonitor
from tools.constants import Constants
from datetime import datetime, timedelta
from download.s2_post_download import SAFE_handler
import sys
import pprint

def get_data(start_date, safe_dir, date_dir):
    """
    Queries and downloads data from all available DK tiles from CDSE.
    Then unzips .SAFE files to a date directory named by "YYYYMMDD".
    Returns a list of tile dir handles with available data for today
    """

    tile_list = Constants.get_tile_list()

    features = []
    for tile_id in tile_list:
        features.append(query_tile(tile_id, start_date))
    
    if not features:
        print(f'## No features available for {datetime.today()}')
        return
    
    for feature in features:
        download_tile(feature, safe_dir, concurrency = 1)


    SAFE_handler.unzip_files(safe_dir)
    available_tiles = SAFE_handler.process_dir(safe_dir, date_dir)
    return available_tiles


def query_tile(tile_id, start_date, processing_level = "S2MSI2A"):
    """
    Query CDSE for a single tile on a single day
    """

    completion_date = start_date + timedelta(days=1)
    completion_date = completion_date.strftime('%Y-%m-%d')

    features = query_features(
        "Sentinel2",
        {
            "startDate": start_date.strftime('%Y-%m-%d'),
            "completionDate": completion_date, 
            "processingLevel": processing_level,
            "cloudCover": "[0,99]",
            "tileId": tile_id
        },
    )
    return features

def download_tile(feature, download_dir, concurrency = 1):
        """
        Download a query from CDSE
        """

        list(
            download_features(
                feature,
                download_dir,
                {
                    "concurrency": concurrency,
                    "monitor": StatusMonitor(),
                    "credentials": Credentials(),
                },
            )
        )

