import os
from tools.vrt_tools import VRTTools
from tools.utils import Utils

class TIFFBurner:
    def __init__(self, mask_32, mask_33):
        self.mask_32 = mask_32
        self.mask_33 = mask_33

    def burn_to_tiff(self, vrt_bands, output_dir, name = None):

        output_tiffs = []
        for vrt in vrt_bands:
            tiff_name = os.path.basename(vrt).replace(".vrt", ".tiff")
            utm = Utils.extract_utm(vrt)

            if utm == 32: mask = self.mask_32
            elif utm ==33: mask = self.mask_33

            output_tif = f"{output_dir}/{tiff_name}"
            output_tiffs.append(output_tif)

            VRTTools.apply_buffer_to_vrt(vrt, output_tif, mask)

            # def apply_buffer_to_vrt(input_vrt, output, mask):

            #     gdal.Open(input_vrt)
            #     gdal.Warp(
            #         output,
            #         input_vrt,
            #         cutlineDSName=mask,
            #         resampleAlg='cubic',
            #         blend=True,
            #         cutlineBlend=24
            #     )

        return output_tiffs