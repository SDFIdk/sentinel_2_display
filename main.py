from datetime import datetime
from osgeo import gdal
import os
import sys
import pathlib
from download.cdse_tile_downloader import get_data
from tools.build_vrts import BuildVRTs
from tools.cloud_mask import CloudMask
from tools.update_rgbi import TIFFBurner
from tools.generate_cut_vrt import cut_vrt
from tools.wms_update import WMSUpdate


#TODO implement a garbage collection system
    #a util which deletes a file list
    #a garbage collect global var to send designated to deletion

def main(safe_dir, garbage_collect):

    pathlib.Path(safe_dir).mkdir(parents=True, exist_ok=True)

    # today = datetime.today()
    today = datetime.strptime("2024-06-07", '%Y-%m-%d').date()    #TEST_DATE WITH DATA
    date_dir = today.strftime('%Y%m%d') + '/'
    pathlib.Path(date_dir).mkdir(parents=True, exist_ok=True)

    rgbi_destination = "X:/2021_Sentinel/RGBI/"
    ndvi_destination = "X:/2021_Sentinel/NDVI/"
    evi_destination = "X:/2021_Sentinel/EVI/"
    lai_destination = "X:/2021_Sentinel/LAI/"
    wms_destination = "V:/"

    gdal.SetConfigOption('GDAL_CACHEMAX', '900')
    gdal.SetConfigOption('COMPRESS_OVERVIEW', 'JPEG')
    gdal.SetConfigOption('JPEG_QUALITY_OVERVIEW', '85')
    gdal.SetConfigOption('INTERLEAVE_OVERVIEW', 'PIXEL')
    gdal.SetConfigOption('BIGTIFF_OVERVIEW', 'YES')

    #maybe rewrite:
    # dict with type:formula
    #var for destination superfolder, subfolders (rgbi, ndvi...) have folder derived from type


    #1run_CDSE_etc
    available_tiles = get_data(start_date = today, safe_dir = safe_dir, date_dir = date_dir, cl = True)
    if not available_tiles: 
        print(f"No data available for {today}")
        return
    #IMPLEMENT COMMAND LINE WISE CDSE DOWNLOAD FUNCTIONALITY

    #2run_buildvrt
    build_vrts = BuildVRTs(available_tiles)
    qc_vrt = build_vrts.build_single_band_vrt(band = 'B02_10m', output = 'Sentinel_DK_B02.vrt')
    scl_vrt = build_vrts.build_single_band_vrt(band = 'SCL_20m', output = 'Sentinel_DK_SCL.vrt')

    rgbi_bands = build_vrts.build_rgbi_vrt()
    ndvi_bands = build_vrts.build_ndvi_vrt()
    evi_bands = build_vrts.build_evi_vrt()
    lai_bands = build_vrts.build_lai_vrt()

    #3CLoud_mask_SCL.bat
    #ALSO HANDLES UPDATE FOOTPRINT FROM STEP 4
    cloud_mask = CloudMask(available_tiles, date_dir, scl_vrt, qc_vrt, today.strftime('%Y%m%d'))
    out_buffer32, out_buffer33, footprint = cloud_mask.scl_to_cloudmask()

    #4update_All_run.bat
    mask_burner = TIFFBurner(out_buffer32, out_buffer33)
    rgbi_tiffs = mask_burner.burn_to_tiff(rgbi_bands, rgbi_destination)
    ndvi_tiffs = mask_burner.burn_to_tiff(ndvi_bands, ndvi_destination)
    evi_tiffs = mask_burner.burn_to_tiff(evi_bands, evi_destination)
    lai_tiffs = mask_burner.burn_to_tiff(lai_bands, lai_destination)
    #are VI bands meant to be part of the LUTs or are they separate files?

    #call Update_RGBI_Gdal_lut.bat
    #also is suppoed to do footprints but thats now handled in scl_to_cloudmask
    rgbi_lut_vrts = [BuildVRTs.lut_vrt_from_rgbi(rgbi) for rgbi in rgbi_tiffs]
    vrt_8bit = cut_vrt(rgbi_lut_vrts)

    #call Update_10km_WMS.bat
    WMSUpdate(vrt_8bit, wms_destination).run()
    # TODO find out how implement copying to V:/ and what the footprint and vms.ovr files are

    #Does another .bat call something beyond 4update?


    
if __name__ == "__main__": 
    main('zip/', garbage_collect=True)