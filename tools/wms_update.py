from tools.utils import Utils

import ast
import pathlib 
import shutil
from osgeo import gdal
import os 

class WMSUpdate:

    def __init__(
            self, 
            input_vrt, 
            date_dir, 
            destination_dir, 
            compress = "JPEG", 
            quality = 85, 
            garbage_collect = False
            ):
        
        self.input_vrt = input_vrt
        self.wms_dir = os.path.join(date_dir, 'wms/')
        self.destination_dir = destination_dir
        pathlib.Path(self.destination_dir).mkdir(parents=True, exist_ok=True)
        with open('constants/wms.txt', 'r') as file:
            self.wms_tiles = ast.literal_eval(file.read())
        self.compress = compress
        self.quality = quality
        self.garbage_collect = garbage_collect

    def run(self):

        def build_overviews(input_vrt):

            ds = gdal.Open(input_vrt, gdal.GA_Update)
            ds.BuildOverviews('average', [2, 4, 10, 25, 50, 100, 200, 500, 1000])

        wms_tiles = []
        for bbox, wms_id in self.wms_tiles.items():

            output_file = os.path.join(self.wms_dir, f"10km_{wms_id}.tif")
            wms_tiles.append(output_file)

            options = gdal.TranslateOptions(
                projWin=bbox,
                xRes=10,
                yRes=10,
                resampleAlg="cubic",
                creationOptions=[
                    f"COMPRESS={self.compress}",
                    f"JPEG_QUALITY={self.quality}",
                    "TILED=YES",
                    "COMPRESS=DEFLATE"
                ]
            )

            gdal.Translate(output_file, self.input_vrt, options=options)

        wms_vrt = os.path.join(self.wms_dir, "sentinel_8bit_RGB_10km.vrt")
        gdal.BuildVRT(
            wms_vrt,
            [gdal.Open(tile) for tile in wms_tiles], 
            )

        build_overviews(wms_vrt)

        shutil.copy(wms_vrt, os.path.join(self.destination_dir, "sentinel_8bit_RGB_10km.vrt"))
        #copy all tiles and overview ("sentinel_8bit_RGB_10km.vrt") to V:/
        #including "sentinel_8bit_RGB_10km.vrt.ovr" which is attained from where???

        #then delete  V:\footprint.* and replace with...
        # copy X:\2021_Sentinel\FOOTPRINT\footprint_20240201.* V:\footprint.*

        if self.garbage_collect: 
            Utils.safer_remove(self.wms_dir)