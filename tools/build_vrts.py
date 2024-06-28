from tools.vrt_tools import VRTTools
from tools.utils import Utils
import os

class BuildVRTs:

    def __init__(self, available_tiles, crs = None):
        self.available_tiles = available_tiles
        self.calc_path = "tools/gdal_calc.py"
        self.utm_32, self.utm_33 = VRTTools.sort_tiles_by_utm(self.available_tiles)
        if not crs: self.crs = 'EPSG:25832' #standard CRS for DK
 

    def build_single_band_vrt(self, band, output):
        """
        Builds a VRT file from similar bands across all available tiles.
        band: Sentinel-2 band name, without ext. (always .jp2)
        output: output filename/path
        """
        
        utm_32_scl_vrt = VRTTools.combine_common_utm_files(
            vrt_input_files = [f"{tile}\{band}.jp2" for tile in self.utm_32],
            output  = f"sentinel_{band}_UTM32_{self.crs}.vrt"
        )
        utm_33_scl_vrt = VRTTools.combine_common_utm_files(
            vrt_input_files = [f"{tile}\{band}.jp2" for tile in self.utm_33],
            output  = f"sentinel_{band}_UTM33_{self.crs}.vrt"
        )

        return VRTTools.combine_vrts([utm_32_scl_vrt, utm_33_scl_vrt], output)
    

    def build_rgbi_vrt(self):
        """
        Builds a vrt with seperate bands from a list of dataset paths
        Output name optional, defaults to RGBI.vrt
        """

        rgbi_bands = []
        for tile in self.available_tiles:
            b4 = os.path.join(tile, '/B04_10m.jp2')
            b3 = os.path.join(tile, '/B03_10m.jp2')
            b2 = os.path.join(tile, '/B02_10m.jp2')
            b8 = os.path.join(tile, '/B08_10m.jp2')

            output = os.path.join(tile, 'RGBI.vrt')

            VRTTools.vrt_from_bands([b4, b3, b2, b8], output)

            rgbi_bands.append(output)

        return rgbi_bands

    def build_ndvi_vrt(self):
        """
        Builds a VRT with separate bands from a list of dataset paths and calculates NDVI.
        Output name optional, defaults to NDVI.vrt.
        """

        ndvi_vrts = []
        for tile in self.available_tiles:
            b4 = os.path.join(tile, '/B04_10m.jp2')
            b8 = os.path.join(tile, '/B08_10m.jp2')

            ndvi_bands = os.path.join(tile, 'ndvi_bands.vrt')
            ndvi_vrt = os.path.join(tile, 'ndvi.vrt')

            VRTTools.vrt_from_bands([b8, b4], ndvi_bands)

            command = [
                self.calc_path,
                "--format=VRT",
                "--type=Float32"
                "-A", ndvi_bands,
                "--A_band=1",
                "-B", ndvi_bands,
                "--B_band=2",
                "--outfile", ndvi_vrt,
                "--calc=\"(A-B)/(A+B)\"",
            ]
            Utils.run_gdal_calc(command)

            ndvi_vrts.append(ndvi_vrt)

        return ndvi_vrts
    
    def build_evi_vrt(self):
        """
        Builds a VRT with separate bands from a list of dataset paths and calculates EVI.
        """
        evi_vrts = []
        for tile in self.available_tiles:
            b2 = os.path.join(tile, 'B02_10m.jp2')
            b4 = os.path.join(tile, 'B04_10m.jp2')
            b8 = os.path.join(tile, 'B08_10m.jp2')

            evi_bands = os.path.join(tile, 'evi_bands.vrt')
            evi_vrt = os.path.join(tile, 'evi.vrt')

            VRTTools.vrt_from_bands([b8, b4, b2], evi_bands)

            command = [
                    "python", self.calc_path,
                    "--format=VRT",
                    "--type=Float32",
                    "-A", evi_bands,
                    "--A_band=1",
                    "-B", evi_bands,
                    "--B_band=2",
                    "-C", evi_bands,
                    "--C_band=3",
                    "--outfile", evi_vrt,
                    "--calc=(2.5 * ((A - B) / (A + 6 * B - 7.5 * C + 1)))"
                ]
            Utils.run_gdal_calc(command)
            
            evi_vrts.append(evi_vrt)

        return evi_vrts
    

    def build_lai_vrt(self):
        """
        Builds a VRT with separate bands from a list of dataset paths and calculates LAI.
        LAI equation: LAI= 3.618 * EVI - 0.118
        Boegh et al. (2002) DOI: https://doi.org/10.1016/S0034-4257(01)00342-X
        """

        lai_vrts = []
        for tile in self.available_tiles:
            b2 = os.path.join(tile, 'B02_10m.jp2')
            b4 = os.path.join(tile, 'B04_10m.jp2')
            b8 = os.path.join(tile, 'B08_10m.jp2')

            lai_bands = os.path.join(tile, 'lai_bands.vrt')
            lai_vrt = os.path.join(tile, 'lai.vrt')

            VRTTools.vrt_from_bands([b8, b4, b2], lai_bands)

            command = [
                "python", self.calc_path,
                "--format=VRT",
                "--type=Float32",
                "-A", lai_bands,
                "--A_band=1",
                "-B", lai_bands,
                "--B_band=2",
                "-C", lai_bands,
                "--C_band=3",
                "--outfile", lai_vrt,
                "--calc=3.618*(2.5*((A-B)/(A+6*B-7.5*C+1)))-0.118"
            ]

            Utils.run_gdal_calc(command)
            lai_vrts.append(lai_vrt)

        return lai_vrts