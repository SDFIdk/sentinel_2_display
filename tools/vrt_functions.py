from osgeo import gdal
import os
import glob
import tempfile
from tools.constants import Constants

class VRTFunctions:

    def combine_common_utm_files(
            vrt_input_files,  
            utm,
            ext = 'jp2', 
            crs = 'EPSG:25832', 
            resample = 'cubic', 
            output = None
            ):
        
        """
        build VRT from files in dir with same UTM crs and warp to CRS
        """

        if not output:
            output = f"sentinel_B02_UTM{utm}_{crs}.vrt"

        with tempfile.NamedTemporaryFile(suffix='.vrt', delete=True, delete_on_close = True) as temp_vrt:
            tmp = temp_vrt.name

            datasets = [gdal.Open(input_file) for input_file in vrt_input_files]

            options = gdal.BuildVRTOptions(srcNodata=0)
            gdal.BuildVRT(tmp, datasets, options=options)

            options = gdal.WarpOptions(
                dstSRS=crs,
                resample=resample
            )
            gdal.Warp(output, tmp, options=options)

        return output
    
    def combine_vrts(input_vrts, output = None):
        if not output:
            output = os.path.commonprefix(input_vrts) + ".tif"
            if not output: output = "common_vrt.tif"

        with tempfile.NamedTemporaryFile(suffix='.vrt', delete=True, delete_on_close = True) as temp_vrt:
            tmp = temp_vrt.name

            datasets = [gdal.Open(input_file) for input_file in input_vrts]
            gdal.BuildVRT(tmp, datasets)

            gdal.Translate(output, tmp, xRes=60, yRes=60)

        return output

    def build_rgbi_vrt(datasets, output = None):
        """
        Builds a vrt with seperate bands from a list of dataset paths
        Output name optional, defaults to RGBI.vrt
        """
        if not output:
            output = "RGBI.vrt"

        datasets = [gdal.Open(input_file) for input_file in datasets]

        gdal.BuildVRT(output, datasets, seperate = True)

    def sort_tiles_by_utm(available_tiles):

        dk_tiles = Constants.get_tile_list()

        #hardcoded for utm zones covering DK 
        utm_32 = []
        utm_33 = []

        #CHECK THAT A TILE ID IS BEING IF'D AND NOT AN ENTIRE PATH. OR SHOULD IT BE THE PATH?
        for tile in available_tiles:
            if tile in dk_tiles:
                try:
                    if tile[1:2] == '32': utm_32.append(tile)
                    elif tile[1:2] == '33': utm_33.append(tile)
                except Exception:
                    print(f'UTM {tile[1:2]} from file {tile} is not a valid zone for DK')

        return utm_32, utm_33
