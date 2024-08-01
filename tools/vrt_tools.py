from osgeo import gdal
import os
import tempfile
import subprocess
from constants.constants import Constants
from tools.utils import Utils
import sys

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

        if len(vrt_input_files) == 0: 
            return None

        datasets = [gdal.Open(input_file) for input_file in vrt_input_files]

        options = gdal.BuildVRTOptions(
            resampleAlg=resample,
            # outputSRS=crs,    #RuntimeError: Translating SRS failed: EPSG:25832      for some reason this thing doesnt recognize EPSG:25832
            srcNodata=0,
        )
        gdal.BuildVRT(output, datasets, options=options)

        #TODO WARP TO CRS SEPARATELY

        return output
    
    
    def combine_vrts(input_vrts, output = None):
        if not output:
            output = os.path.commonprefix(input_vrts) + ".tif"
            if not output: output = "common_vrt.tif"

        with tempfile.NamedTemporaryFile(suffix='.vrt', delete=False) as temp_vrt:
            tmp = temp_vrt.name

        datasets = [gdal.Open(input_file) for input_file in input_vrts if input_file is not None]

        gdal.BuildVRT(tmp, datasets)#.close()
        gdal.Translate(output, tmp, xRes=60, yRes=60)

        return output


    def sort_tiles_by_utm(available_tiles):

        dk_tiles = Constants.get_tile_list()
        
        #hardcoded for utm zones covering DK 
        utm_32 = []
        utm_33 = []

        for tile in available_tiles:
            tile_id = os.path.basename(tile)
            if tile_id in dk_tiles:
                utm = tile_id[:2]

                try:
                    if utm == '32': utm_32.append(tile)
                    elif utm == '33': utm_33.append(tile)
                except Exception:
                    print(f'UTM {tile_id[1:2]} from file {tile_id} is not a valid zone for DK')

        return utm_32, utm_33
    

    def vrt_from_bands(band_list, output, resample = 'cubic', separate = True):

        datasets = [gdal.Open(band) for band in band_list]

        options = gdal.BuildVRTOptions(
            resampleAlg=resample, 
            separate=separate
            )
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


    def convert_to_8bit(input_tif, eightbit_output):
        
        gdal.Translate(
            eightbit_output,
            input_tif,
            outputType=gdal.GDT_Byte,
            scaleParams=[
                [0, 7500, 0, 255],
                [0, 7500, 0, 255],
                [0, 7500, 0, 255],
                [0, 10000, 0, 255]
            ]
        )


    # def build_lut(input_vrt, lut_instructions, gdal_lut = "tools/gdal_lut.py"):

        # # install gdal lut somehow? Can this be a file to be included in the package like calc?
        # # is it related to this https://github.com/sudhirmurthy/gdal-examples/blob/master/gdal_lut.py   ?

        # outputs_bands = []
        # for i, lut in enumerate(lut_instructions, start=1):
        #     output_lut_tif = input_vrt.replace(".tif", f"_{i}.tif")
        #     outputs_bands.append(output_lut_tif)
        #     subprocess.run([
        #         gdal_lut,
        #         input_vrt,
        #         "-srcband", str(i), 
        #         output_lut_tif,
        #         "-lutfile", lut
        #     ])

        # # TODO recombine output_bands to vrt

        # return outputs_bands

    def apply_lut_to_bands(input_tif, lut_instructions, gdal_lut_script='tools/gdal_lut.py'):
        """
        Apply LUT to each band of a TIFF file using the gdal_lut.py script.

        Parameters:
        - input_tif (str): Path to the input TIFF file.
        - lut_instructions (list): List of paths to the LUT text files, one for each band.
        - gdal_lut_script (str): Path to the gdal_lut.py script.
        """
        for band_index, lut_file in enumerate(lut_instructions, start=1):
            output_file = f"{input_tif.split('.')[0]}_band{band_index}_lut.tif"
            
            cmd = [
                'python', gdal_lut_script,
                input_tif, '-srcband', str(band_index),
                output_file, '-dstband', '1',
                '-lutfile', lut_file,
                '-of', 'GTiff'
            ]
            
            print(f"Applying LUT to band {band_index} using {lut_file}")
            subprocess.run(cmd, check=True)
