from osgeo import gdal
import os
import tempfile
from constants.constants import Constants
from tools.utils import Utils

class VRTTools:

    def combine_common_utm_files(
            vrt_input_files,  
            output,
            crs = 'EPSG:25832', 
            resample = 'cubic', 
            ):
        """
        Build VRT from files in dir with same UTM crs and warp to CRS
        """

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


    def sort_tiles_by_utm(available_tiles):

        dk_tiles = Constants.get_tile_list()

        #hardcoded for utm zones covering DK 
        utm_32 = []
        utm_33 = []

        #CHECK THAT A TILE ID IS A PATH AND THAT EVERYTHING WORKS WITH THAT
        for tile in available_tiles:
            if tile in dk_tiles:
                utm = Utils.extract_utm(tile)
                try:
                    if utm == '32': utm_32.append(tile)
                    elif utm == '33': utm_33.append(tile)
                except Exception:
                    print(f'UTM {tile[1:2]} from file {tile} is not a valid zone for DK')

        return utm_32, utm_33
    

    def vrt_from_bands(band_list, output, resample = 'cubic'):

        datasets = [gdal.Open(band) for band in band_list]

        options = gdal.WarpOptions(resample=resample, separate = True)
        gdal.BuildVRT(output, datasets, options=options)


    def apply_buffer_to_vrt(input_vrt, output, mask):

        gdal.Open(input_vrt)
        gdal.Warp(
            output,
            input_vrt,
            cutlineDSName=mask,
            resampleAlg='cubic',
            blend=True,
            cutlineBlend=24
        )
