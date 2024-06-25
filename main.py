from datetime import datetime
import os
from download.cdse_tile_downloader import cdse_tile_downloader
from download.s2_post_download import SAFE_handler
from tools.vrt_functions import VRTFunctions
from tools.constants import Constants

def get_data(start_date, safe_dir, date_dir):

    cdse_tile_downloader(start_date, safe_dir)
    SAFE_handler.unzip_files(safe_dir)
    available_tiles = SAFE_handler.process_dir(safe_dir, date_dir)
    return available_tiles

def sort_tiles_by_utm(available_tiles):

    dk_tiles = Constants.get_tile_list()

    #hardcoded for utm zones 32, 33
    utm_32 = []
    utm_33 = []
    #CHECK THAT A TILE ID IS BEING IF'D AND NOT AN ENTIRE PATH.
    for tile in available_tiles:
        if tile in dk_tiles:
            try:
                if tile[1:2] == '32': utm_32.append(tile)
                elif tile[1:2] == '33': utm_33.append(tile)
            except Exception:
                print(f'UTM {tile[1:2]} from file {tile} is not a valid zone for DK')

    return utm_32, utm_33

def build_qc_vrt(available_tiles):

    utm_32, utm_33 = sort_tiles_by_utm(available_tiles)
    
    utm_32_qc_vrt = VRTFunctions.combine_common_utm_files(
        [f"{tile}\B02_10m.jp2" for tile in utm_32],
        utm = 32
    )
    utm_33_qc_vrt = VRTFunctions.combine_common_utm_files(
        [f"{tile}\B02_10m.jp2" for tile in utm_33],
        utm = 33
    )
    return VRTFunctions.combine_vrts([utm_32_qc_vrt, utm_33_qc_vrt])

    
def build_scl_vrt(available_tiles):

    utm_32, utm_33 = sort_tiles_by_utm(available_tiles)
    
    utm_32_scl_vrt = VRTFunctions.combine_common_utm_files(
        [f"{tile}\SCL_20m.jp2" for tile in utm_32],
        utm = 32
    )
    utm_33_scl_vrt = VRTFunctions.combine_common_utm_files(
        [f"{tile}\SCL_10m.jp2" for tile in utm_33],
        utm = 33
    )
    return VRTFunctions.combine_vrts([utm_32_scl_vrt, utm_33_scl_vrt])





if __name__ == "__main__":

    start_date = datetime.today().strftime('%Y-%m-%d')

    safe_dir = 'zip'
    os.mkdir(safe_dir)

    today = datetime.today().strftime('%Y%m%d')
    date_dir = today + '/'
    os.mkdir(date_dir)

    available_tiles = get_data(
        start_date = datetime.today().strftime('%Y-%m-%d'), 
        safe_dir = safe_dir, 
        date_dir = date_dir
        )
    
    qc_vrt = build_qc_vrt(available_tiles)
    scl_vrt = build_qc_vrt(available_tiles)


    # utm_32_scl_files.append(f"{tile}\SCL_20m.jp2")
    # utm_32_b11_files.append(f"{tile}\B11_20m.jp2")
    
    #implement 2run_buildvrt.bat



    #implement 3CLoud_mask_SCL.bat
