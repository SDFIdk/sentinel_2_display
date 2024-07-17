from datetime import datetime
from osgeo import gdal
import os
import sys
import pathlib
from download.data_acquisition import get_data
from tools.build_vrts import BuildVRTs
from tools.cloud_mask import CloudMask
from tools.burn_tiff import TIFFBurner
from tools.generate_cut_vrt import cut_vrt
from tools.wms_update import WMSUpdate
from tools.utils import Utils


#TODO implement a garbage collection system
    #a util which deletes a file list
    #a garbage collect global var to send designated to deletion

def main(safe_dir, garbage_collect = False):

    gdal.UseExceptions()

    pathlib.Path(safe_dir).mkdir(parents=True, exist_ok=True)

    # today = datetime.today()
    today = datetime.strptime("2020-02-04", '%Y-%m-%d').date()    #TEST_DATE WITH DATA
    date_dir = today.strftime('%Y%m%d') + '/'
    pathlib.Path(date_dir).mkdir(parents=True, exist_ok=True)

    rgbi_destination = os.path.join(date_dir, 'rgbi')
    ndvi_destination = os.path.join(date_dir, 'ndvi')
    evi_destination = os.path.join(date_dir, 'evi')
    lai_destination = os.path.join(date_dir, 'lai')
    wms_destination = 'WMS_OUTPUT'

    gdal.SetConfigOption('GDAL_CACHEMAX', '900')
    gdal.SetConfigOption('COMPRESS_OVERVIEW', 'JPEG')
    gdal.SetConfigOption('JPEG_QUALITY_OVERVIEW', '85')
    gdal.SetConfigOption('INTERLEAVE_OVERVIEW', 'PIXEL')
    gdal.SetConfigOption('BIGTIFF_OVERVIEW', 'YES')

    #TODO ENSURE THERE ARE NO TODOS IN THE SCRIPT!
    #TODO ENSURE CORRECT CRS IS SET, SEE TODO IN vrt_tools, combine_common_utm_files
    #TODO ENSURE SCRIPT CAN HANDLE DATA IN ONE UTM BUT NOT THE OTHER
    #TODO ASK ABOUT THE GDAL LUT APPLICATION, WHERE DO I GET IT FROM?
    #TODO ENABLE VI SCRIPTS SOMEHOW, CHECK ndvi_tools.py FOR A NON-CALC SOLUTION

    #1run_CDSE_etc
    available_tiles = get_data(
        start_date = today, 
        safe_dir = safe_dir, 
        date_dir = date_dir, 
        garbage_collect = garbage_collect
        )
    
    if not available_tiles: 
        print(f"No data available for {today}")
        return

    #2run_buildvrt
    build_vrts = BuildVRTs(available_tiles)
    qc_vrt = build_vrts.build_single_band_vrt(band = 'B02_10m', output = 'Sentinel_DK_B02.vrt')
    scl_vrt = build_vrts.build_single_band_vrt(band = 'SCL_20m', output = 'Sentinel_DK_SCL.vrt')

    rgbi_bands = build_vrts.build_rgbi_vrt()
    ndvi_bands = build_vrts.build_ndvi_vrt()
    # evi_bands = build_vrts.build_evi_vrt()
    sys.exit()
    lai_bands = build_vrts.build_lai_vrt()

    if garbage_collect: Utils.safer_remove(safe_dir)

    #3CLoud_mask_SCL.bat
    #ALSO HANDLES UPDATE FOOTPRINT FROM STEP 4
    cloud_mask = CloudMask(available_tiles, date_dir, scl_vrt, qc_vrt, today.strftime('%Y%m%d'), garbage_collect = garbage_collect)
    out_buffer32, out_buffer33, footprint = cloud_mask.scl_to_cloudmask()
    print('CHECKPOINT');   sys.exit()  #CHECKPOINT

    #4update_All_run.bat
    mask_burner = TIFFBurner(out_buffer32, out_buffer33, garbage_collect = garbage_collect)
    rgbi_tiffs = mask_burner.burn_to_tiff(rgbi_bands, rgbi_destination)
    # ndvi_tiffs = mask_burner.burn_to_tiff(ndvi_bands, ndvi_destination)
    # evi_tiffs = mask_burner.burn_to_tiff(evi_bands, evi_destination)
    # lai_tiffs = mask_burner.burn_to_tiff(lai_bands, lai_destination)
    #are VI bands meant to be part of the LUTs or are they separate files?

    if garbage_collect:
        Utils.safer_remove(rgbi_bands)
        Utils.safer_remove(ndvi_bands)
        Utils.safer_remove(evi_bands)
        Utils.safer_remove(lai_bands)

    #call Update_RGBI_Gdal_lut.bat
    #also is suppoed to do footprints but thats now handled in scl_to_cloudmask
    rgbi_lut_vrts = [BuildVRTs.lut_vrt_from_rgbi(rgbi) for rgbi in rgbi_tiffs]
    vrt_8bit = cut_vrt(rgbi_lut_vrts)

    #call Update_10km_WMS.bat
    WMSUpdate(vrt_8bit, wms_destination).run()
    # TODO find out how implement copying to V:/ and what the footprint and vms.ovr files are

    #Does another .bat call something beyond 4update?


    
if __name__ == "__main__": 
    main('zip/', garbage_collect=False)