from tools.vrt_tools import VRTTools
import os

class BuildVRTs:

    def __init__(self, available_tiles):
        self.available_tiles = available_tiles
    
    def build_qc_vrt(self):

        utm_32, utm_33 = VRTTools.sort_tiles_by_utm(self.available_tiles)
        
        utm_32_qc_vrt = VRTTools.combine_common_utm_files(
            [f"{tile}\B02_10m.jp2" for tile in utm_32],
            utm = 32
        )
        utm_33_qc_vrt = VRTTools.combine_common_utm_files(
            [f"{tile}\B02_10m.jp2" for tile in utm_33],
            utm = 33
        )
        #name hardcoded for backwards compatibility
        return VRTTools.combine_vrts([utm_32_qc_vrt, utm_33_qc_vrt], 'Sentinel_DK_B02.vrt')

        
    def build_scl_vrt(self):

        utm_32, utm_33 = VRTTools.sort_tiles_by_utm(self.available_tiles)
        
        utm_32_scl_vrt = VRTTools.combine_common_utm_files(
            [f"{tile}\SCL_20m.jp2" for tile in utm_32],
            utm = 32
        )
        utm_33_scl_vrt = VRTTools.combine_common_utm_files(
            [f"{tile}\SCL_10m.jp2" for tile in utm_33],
            utm = 33
        )
        #name hardcoded for backwards compatibility
        return VRTTools.combine_vrts([utm_32_scl_vrt, utm_33_scl_vrt], 'Sentinel_DK_SCL.vrt')
    

    def build_rgbi_vrt(self):
        """
        Builds a vrt with seperate bands from a list of dataset paths
        Output name optional, defaults to RGBI.vrt
        """

        rgbi_bands = []
        for tile in self.available_tiles:
            b4 = os.path.join(tile, '\B04_10m.jp2')
            b3 = os.path.join(tile, '\B03_10m.jp2')
            b2 = os.path.join(tile, '\B02_10m.jp2')
            b8 = os.path.join(tile, '\B08_10m.jp2')

            output = os.path.join(tile, 'RGBI.vrt')

            VRTTools.vrt_from_bands([b4, b3, b2, b8], output)

            rgbi_bands.append(output)

        return rgbi_bands
