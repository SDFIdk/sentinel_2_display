from osgeo_utils import gdal_calc
from tools.cloud_mask_tools import CMTools
from tools.utils import Utils
import os
import sys
import pathlib

class CloudMask():

    def __init__(
            self, 
            available_tiles, 
            date_dir, 
            scl_band, 
            qc_band, 
            today, 
            calc_path = "tools/gdal_calc.py", 
            garbage_collect = False,
        ):

        self.available_tiles = available_tiles
        self.date_dir = date_dir
        self.cloud_dir = os.path.join(date_dir + "cloud_mask")
        pathlib.Path(self.cloud_dir).mkdir(parents=True, exist_ok=True)

        self.scl = scl_band
        self.qc = qc_band
        self.today = today
        self.calc_path = calc_path
        self.garbage_collect = garbage_collect


    def scl_to_cloudmask(self):
        scl_tif = os.path.join(self.cloud_dir,  "SCL01.tif")
        scl_250 = os.path.join(self.cloud_dir,  "SCL01_250m.tif")
        cloud_nodata = os.path.join(self.cloud_dir, "cloud_and_nodata.shp")
        cloud_nodata_mask = os.path.join(self.cloud_dir, "cloud_and_nodata_mask.shp")
        footprint_60 = os.path.join(self.cloud_dir, "footprint_60.tif")
        out_mask = os.path.join(self.cloud_dir, "out_mask.shp")
        out_mask_32 = os.path.join(self.cloud_dir, "out_mask32")
        out_mask_33 = os.path.join(self.cloud_dir, "out_mask33")

        gdal_calc.Calc(
            calc = "(A<=6)*0 + (A>=7)*(A<=10)*1 + (A>10)*0",    #set all non-cloud values to zero
            A = self.scl,
            A_band = 1,
            outfile = scl_tif,
            overwrite = True,
            format = "GTiff",
        )

        CMTools.resolution_averaging(input_file = scl_tif, output_file = scl_250)
        CMTools.polygonalize_tif(input_file = scl_250, output_file = cloud_nodata)
        CMTools.buffer_nodata(input_file = cloud_nodata, output_file = cloud_nodata_mask)

        gdal_calc.Calc(
            calc = f"0*(A<=0.01) + (A>0.01)*{self.today}",
            A = scl_tif,
            A_band = 1,
            outfile = footprint_60,
            overwrite = True,
            format = "GTiff",
            type = "Float32"
        )

        CMTools.burn_cloudmask(input_shapefile = cloud_nodata_mask, output_file = footprint_60, burn_value = self.today, inverse = True)
        CMTools.burn_cloudmask(cloud_nodata_mask, footprint_60, 0)
        CMTools.polygonalize_tif(footprint_60, out_mask)
        print(footprint_60)
        print(out_mask_32)

        #FIXME GDAL CAN NO LONGER PROCESS ANY EPSGS.

        CMTools.translate_vector(out_mask, out_mask_32, "EPSG:32632")
        CMTools.translate_vector(out_mask, out_mask_33, "EPSG:32633")
        print('FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! ')
        print('FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! ')
        print('FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! FAIL PASSED !!! ')

        #Update footprint
        footprint = CMTools.update_footprint(footprint_60, "FOOTPRINT", self.today)

        if self.garbage_collect:
            Utils.safer_remove(scl_250)
            Utils.safer_remove(scl_tif)
            Utils.safer_remove(cloud_nodata)
            Utils.safer_remove(cloud_nodata_mask)
            Utils.safer_remove(footprint_60)
            Utils.safer_remove(out_mask)
   
        return out_mask_32, out_mask_33, footprint