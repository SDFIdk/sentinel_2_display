from datetime import datetime
import os
import sys
import pathlib
from download.cdse_tile_downloader import get_data
from tools.build_vrts import BuildVRTs

def main(safe_dir):

    pathlib.Path(safe_dir).mkdir(parents=True, exist_ok=True)

    # today = datetime.today()
    today = datetime.strptime("2024-06-07", '%Y-%m-%d').date()    #TEST_DATE WITH DATA

    date_dir = today.strftime('%Y%m%d') + '/'
    pathlib.Path(date_dir).mkdir(parents=True, exist_ok=True)

    available_tiles = get_data(start_date = today, safe_dir = safe_dir, date_dir = date_dir)
    
    qc_vrt = BuildVRTs.build_qc_vrt(available_tiles)
    scl_vrt = BuildVRTs.build_qc_vrt(available_tiles)
    
    #implement 2run_buildvrt.bat
    #implement 3CLoud_mask_SCL.bat



if __name__ == "__main__": 
    main('zip/')