import itertools

from cdsetool.query import query_features
from cdsetool.credentials import Credentials
from cdsetool.download import download_features
from cdsetool.monitor import StatusMonitor
from tools.constants import Constants
from datetime import datetime, timedelta
import sys
import pprint

# call cdsetool download Sentinel2 zip --concurrency 4 --search-term tileId=33VUD --search-term startDate=2024-03-06 --search-term completionDate=2024-03-07 --search-term processingLevel=S2MSI2A


def cdse_tile_downloader(start_date, download_dir, tile_list = None, processing_level = "S2MSI2A", concurrency = 1):

    def query_tile(tile_id, start_date, processing_level):

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

    def download_tiles(features, download_dir, concurrency = 1):

        for feature in features:
            list(
                download_features(
                    feature,
                    download_dir,
                    {
                        "concurrency": concurrency,
                        # "monitor": StatusMonitor(),
                        "credentials": Credentials(),
                    },
                )
            )
            print('aaaa')
            sys.exit()
    
    if not tile_list:
        tile_list = Constants.get_tile_list()

    features = []
    for tile_id in tile_list:
        features.append(query_tile(tile_id, start_date, processing_level))
    
    if not features:
        print(f'## No features available for {datetime.today()}')
        return
    
    download_tiles(features, download_dir, concurrency)
