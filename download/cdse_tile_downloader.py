from cdsetool.query import query_features
from cdsetool.credentials import Credentials
from cdsetool.download import download_features, download_feature
from cdsetool.monitor import StatusMonitor
from constants.constants import Constants
from datetime import datetime, timedelta
from download.s2_post_download import SAFE_handler
import sys
import argparse
import subprocess
import datetime
import glob

def get_data(start_date, safe_dir, date_dir, cl = False):
    """
    Queries and downloads data from all available DK tiles from CDSE.
    Then unzips .SAFE files to a date directory named by "YYYYMMDD".
    Returns a list of tile dir handles with available data for today

    cl option downloads by command line via argparse. This may 
    """

    tile_list = Constants.get_tile_list()

    if cl:
        download_tile_cl(features, safe_dir, concurrency = 1)
    else:
        features = []
        for tile_id in tile_list:
            features.append(query_tile(tile_id, start_date))

        download_tiles(features, safe_dir, concurrency = 1)

    if not glob.glob(safe_dir + '*.zip'):
        print(f'## No features available for {datetime.today()}')
        return
    

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

def download_tiles(features, download_dir, concurrency = 1):
        """
        Download a query from CDSE
        """
        #switch to single item mode at some point
        # for feature in features:
        #     print(feature.get('id'))
        #     download_feature(
        #         feature, 
        #         download_dir
        #         )

        for feature in features:
            list(
                download_features(
                    feature,
                    download_dir,
                    {
                        "concurrency": concurrency,
                        #"monitor": StatusMonitor(),
                        "credentials": Credentials(),
                    },
                )
            )

def download_tile_cl(dk_tiles, download_dir, concurrency = 1):
    parser = argparse.ArgumentParser(description="Download Sentinel-2 data using cdsetool.")
    parser.add_argument("--concurrency", type=int, required=True, help="Number of concurrent downloads.")
    parser.add_argument("--search-term", action='append', required=True, help="Search term in the format key=value.")
    
    args = parser.parse_args()
    
    search_terms = []
    for term in args.search_term:
        search_terms.extend(["--search-term", term])
    
    command = [
        "cdsetool", "download", "Sentinel2", "zip",
        "--concurrency", str(args.concurrency)
    ] + search_terms

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

#fix this later...