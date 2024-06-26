from datetime import datetime
import os
import sys
import pathlib
from download.cdse_tile_downloader import get_data
from tools.build_vrts import BuildVRTs
from tools.cloud_mask import CloudMask

def main(safe_dir):

    pathlib.Path(safe_dir).mkdir(parents=True, exist_ok=True)

    # today = datetime.today()
    today = datetime.strptime("2024-06-07", '%Y-%m-%d').date()    #TEST_DATE WITH DATA

    date_dir = today.strftime('%Y%m%d') + '/'
    pathlib.Path(date_dir).mkdir(parents=True, exist_ok=True)

    available_tiles = get_data(start_date = today, safe_dir = safe_dir, date_dir = date_dir)

    build_vrts = BuildVRTs(available_tiles)
    qc_vrt = build_vrts.build_qc_vrt()
    scl_vrt = build_vrts.build_qc_vrt()
    rgbi_bands = build_vrts.build_rgbi_vrt()

    #implement 3CLoud_mask_SCL.bat
    cloud_mask = CloudMask(available_tiles, scl_vrt, qc_vrt, today.strftime('%Y%m%d'))
    scl_cloud_mask = cloud_mask.scl_to_cloudmask()






if __name__ == "__main__": 
    main('zip/')