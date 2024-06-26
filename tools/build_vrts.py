from tools.vrt_functions import VRTFunctions

class BuildVRTs:

    def build_qc_vrt(available_tiles):

        utm_32, utm_33 = VRTFunctions.sort_tiles_by_utm(available_tiles)
        
        utm_32_qc_vrt = VRTFunctions.combine_common_utm_files(
            [f"{tile}\B02_10m.jp2" for tile in utm_32],
            utm = 32
        )
        utm_33_qc_vrt = VRTFunctions.combine_common_utm_files(
            [f"{tile}\B02_10m.jp2" for tile in utm_33],
            utm = 33
        )
        return VRTFunctions.combine_vrts([utm_32_qc_vrt, utm_33_qc_vrt])

        
    def build_scl_vrt(available_tiles):

        utm_32, utm_33 = VRTFunctions.sort_tiles_by_utm(available_tiles)
        
        utm_32_scl_vrt = VRTFunctions.combine_common_utm_files(
            [f"{tile}\SCL_20m.jp2" for tile in utm_32],
            utm = 32
        )
        utm_33_scl_vrt = VRTFunctions.combine_common_utm_files(
            [f"{tile}\SCL_10m.jp2" for tile in utm_33],
            utm = 33
        )
        return VRTFunctions.combine_vrts([utm_32_scl_vrt, utm_33_scl_vrt])