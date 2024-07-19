from osgeo_utils import gdal_calc
from tools.cloud_mask_tools import CMTools
from tools.utils import Utils
import os
import sys
import pathlib

class CloudMask():

    def __init__(self, available_tiles, working_dir, scl_band, qc_band, today, garbage_collect = False):
        self.available_tiles = available_tiles
        self.working_dir = working_dir
        self.cloud_dir = os.path.join(working_dir + "cloud_mask")
        pathlib.Path(self.cloud_dir).mkdir(parents=True, exist_ok=True)
        self.calc_path = "tools\\gdal_calc.py"
        self.garbage_collect = garbage_collect

        self.scl = scl_band
        self.qc = qc_band
        self.today = today


    def scl_to_cloudmask(self):
        scl_tif = os.path.join(self.cloud_dir,  "SCL01.tif")
        scl_250 = os.path.join(self.cloud_dir,  "SCL01_250m.tif")
        cloud_nodata = os.path.join(self.cloud_dir, "cloud_and_nodata.shp")
        cloud_nodata_buffer = os.path.join(self.cloud_dir, "cloud_and_nodata_buffer.shp")
        footprint_60 = os.path.join(self.cloud_dir, "footprint_60.tif")
        out_buffer = os.path.join(self.cloud_dir, "out_buffer.shp")
        out_buffer_32 = os.path.join(self.cloud_dir, "out_buffer32")
        out_buffer_33 = os.path.join(self.cloud_dir, "out_buffer33")

        gdal_calc.Calc(
            calc = "(A<=6)*0 + (A>=7)*(A<=10)*1 + (A>10)*0",
            A = self.scl,
            A_band = 1,
            outfile = scl_tif,
            overwrite = True,
            format = "GTiff",
        )

        CMTools.resolution_averaging(scl_tif, scl_250)
        CMTools.polygonalize_tif(scl_250, cloud_nodata)

        CMTools.buffer_nodata(cloud_nodata, cloud_nodata_buffer)

        gdal_calc.Calc(
            calc = f"0*(A<=0.01) + (A>0.01)*{self.today}",
            A = self.scl,
            A_band = 1,
            outfile = footprint_60,
            overwrite = True,
            format = "GTiff",
            type = "Float32"
        )

        CMTools.burn_cloudbuffer(cloud_nodata_buffer, footprint_60, self.today, inverse = True)
        CMTools.burn_cloudbuffer(cloud_nodata_buffer, footprint_60, 0)
        CMTools.polygonalize_tif(footprint_60, out_buffer)
        print(footprint_60)
        print(out_buffer_32)

        #FIXME GDAL CAN NO LONGER PROCESS EPSGS. SEE FIX IN FIREFOX BOOKMARK

        CMTools.translate_vector(out_buffer, out_buffer_32, "EPSG:4326")
        CMTools.translate_vector(out_buffer, out_buffer_33, "EPSG:4326")
        print('FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! ')
        print('FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! ')
        print('FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! ')

        #Update footprint
        footprint = CMTools.update_footprint(footprint_60, "FOOTPRINT", self.today)

        if self.garbage_collect:
            Utils.safer_remove(scl_250)
            Utils.safer_remove(scl_tif)
            Utils.safer_remove(cloud_nodata)
            Utils.safer_remove(cloud_nodata_buffer)
            Utils.safer_remove(footprint_60)
            Utils.safer_remove(out_buffer)
   
        return out_buffer_32, out_buffer_33, footprint