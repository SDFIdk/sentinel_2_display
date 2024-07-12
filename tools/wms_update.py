import ast
import pathlib 
from osgeo import gdal
import os 

class WMSUpdate:

    def __init__(self, input_tif, wms_destination, compress = "JPEG", quality = 85):
        self.input_tif = input_tif
        self.wms_destination = wms_destination
        with open('constants/wms.txt', 'r') as file:
            self.wms_tiles = ast.literal_eval(file.read())
        self.compress = compress
        self.quality = quality

        


    def run(self):

        def build_overviews(input_vrt):

            ds = gdal.Open(input_vrt, gdal.GA_Update)
            ds.BuildOverviews('average', [2, 4, 10, 25, 50, 100, 200, 500, 1000])


        pathlib.Path(self.wms_destination).mkdir(parents=True, exist_ok=True)

        wms_tiles = []
        for i, bbox, wms_id in enumerate(self.wms_tiles.items()):

            output_file = os.path.join(self.wms_destination, f"10km_{wms_id}.tif")
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

            gdal.Translate(output_file, self.input_tif, options=options)

        wms_vrt = os.path.join(self.wms_destination, "sentinel_8bit_RGB_10km.vrt")
        gdal.BuildVRT(
            wms_vrt,
            [gdal.Open(tile) for tile in wms_tiles], 
            )

        build_overviews(wms_vrt)

        #copy all tiles and overview ("sentinel_8bit_RGB_10km.vrt") to V:/
        #including "sentinel_8bit_RGB_10km.vrt.ovr" which is attained from where???

        #then delete  V:\footprint.* and replace with...
        # copy X:\2021_Sentinel\FOOTPRINT\footprint_20240201.* V:\footprint.*