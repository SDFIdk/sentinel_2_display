from osgeo import gdal
from datetime import datetime, timedelta
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

gdal.UseExceptions()
gdal.SetConfigOption('GDAL_CACHEMAX', '900')
gdal.SetConfigOption('COMPRESS_OVERVIEW', 'JPEG')
gdal.SetConfigOption('JPEG_QUALITY_OVERVIEW', '85')
gdal.SetConfigOption('INTERLEAVE_OVERVIEW', 'PIXEL')
gdal.SetConfigOption('BIGTIFF_OVERVIEW', 'YES')

    #

    #TODO ENSURE THERE ARE NO TODOS IN THE SCRIPT!

    #TODO TEST GARBAGE_COLLECT
    #TODO ENSURE SCRIPT CAN HANDLE EMPTY UTM LISTS
    #TODO ENSURE CORRECT CRS IS SET, SEE TODO IN vrt_tools, combine_common_utm_files

    #TODO ASK ABOUT THE GDAL LUT APPLICATION, WHERE DO I GET IT FROM?

    #TODO ENABLE VI SCRIPTS SOMEHOW, CHECK ndvi_tools.py FOR A NON-CALC SOLUTION
        #LOOK INTO THE ALTERNATIVE GDAL CALC VERSION IN build_ndvi_vrt
        #OUTPUTTING FROM THERE TO GTIFF INSTEAD OF VRT SHOULD BE COMPATIBLE WITH THE MASKBURNER

def main(working_dir, destination_dir, garbage_collect = False):

    safe_dir = os.path.join(working_dir, 'zip/')
    pathlib.Path(safe_dir).mkdir(parents=True, exist_ok=True)

    # working_date = datetime.today() - timedelta(days = 4)
    working_date = datetime.strptime("2020-02-04", '%Y-%m-%d').date()    #TEST_DATE WITH DATA
    date_dir = working_date.strftime('%Y%m%d') + '/'
    pathlib.Path(date_dir).mkdir(parents=True, exist_ok=True)

     
    rgbi_destination = os.path.join(date_dir, 'rgbi')
    #VI bands will be handled once core functionality is in place
    #TODO Should VIs also be sent to WMS destination folder?
    # ndvi_destination = os.path.join(wms_destination, 'ndvi')
    # evi_destination = os.path.join(wms_destination, 'evi')
    # lai_destination = os.path.join(wms_destination, 'lai')

    #1run_CDSE_etc
    available_tiles = get_data(
        start_date = working_date, 
        safe_dir = safe_dir, 
        date_dir = date_dir, 
        garbage_collect = garbage_collect
        )
    
    if not available_tiles: 
        print(f"No data available for {working_date}")
        return

    #2run_buildvrt
    build_vrts = BuildVRTs(available_tiles, garbage_collect = garbage_collect)

    qc_vrt = build_vrts.build_single_band_vrt(band = 'B02_10m', output = f'{date_dir}/Sentinel_DK_B02.vrt')
    scl_vrt = build_vrts.build_single_band_vrt(band = 'SCL_20m', output = f'{date_dir}/Sentinel_DK_SCL.vrt')

    rgbi_bands = build_vrts.build_rgbi_vrt()

    # ndvi_bands = build_vrts.build_ndvi_vrt()
    # evi_bands = build_vrts.build_evi_vrt()
    # lai_bands = build_vrts.build_lai_vrt()

    if garbage_collect: Utils.safer_remove(safe_dir)

    #3CLoud_mask_SCL.bat
    #ALSO HANDLES UPDATE FOOTPRINT FROM STEP 4
    cloud_mask = CloudMask(available_tiles, date_dir, scl_vrt, qc_vrt, working_date.strftime('%Y%m%d'), garbage_collect = garbage_collect)
    out_buffer32, out_buffer33, footprint = cloud_mask.scl_to_cloudmask()
    print('CHECKPOINT');   sys.exit()  #CHECKPOINT

    #4update_All_run.bat
    mask_burner = TIFFBurner(out_buffer32, out_buffer33, garbage_collect = garbage_collect)
    rgbi_tiffs = mask_burner.burn_to_tiff(rgbi_bands, rgbi_destination)
    
    # ndvi_tiffs = mask_burner.burn_to_tiff(ndvi_bands, ndvi_destination)
    # evi_tiffs = mask_burner.burn_to_tiff(evi_bands, evi_destination)
    # lai_tiffs = mask_burner.burn_to_tiff(lai_bands, lai_destination)
    #TODO are VI bands meant to be part of the LUTs or are they separate files?

    if garbage_collect:
        Utils.safer_remove(rgbi_bands)
        Utils.safer_remove(ndvi_bands)
        Utils.safer_remove(evi_bands)
        Utils.safer_remove(lai_bands)

    #call Update_RGBI_Gdal_lut.bat
    #also is suppoed to do footprints but thats now handled in scl_to_cloudmask

    #BOGMÆRKE

    rgbi_lut_vrts = [BuildVRTs.lut_vrt_from_rgbi(rgbi) for rgbi in rgbi_tiffs]
    vrt_8bit = cut_vrt(rgbi_lut_vrts)

    #call Update_10km_WMS.bat
    WMSUpdate(vrt_8bit, date_dir, destination_dir, garbage_collect=garbage_collect).run()
    # TODO find out how implement copying to V:/ and what the footprint and vms.ovr files are


if __name__ == "__main__": 

    safe_dir = './'
    destination_dir = 'WMS_OUTPUT/',


    main(
        working_dir = safe_dir, 
        destination_dir = destination_dir, 
        garbage_collect=False
        )