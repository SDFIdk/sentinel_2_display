from osgeo import gdal

def cut_vrt(vrt_list):

    # Constants
    # input_file_list_32 = "X:\\2021_Sentinel\\RGBI\\rgbi_vrt32_8bit.txt"
    # input_file_list_33 = "X:\\2021_Sentinel\\RGBI\\rgbi_vrt33_8bit.txt"

    # output names
    # output_vrt_32 = "Sentinel_DK_32632_8bit.vrt"
    # output_vrt_33 = "Sentinel_DK_32633_8bit.vrt"

    gdal.BuildVRT(output_vrt_32, open(input_file_list_32).read().splitlines(), srcNodata=0)
    gdal.BuildVRT(output_vrt_33, open(input_file_list_33).read().splitlines(), srcNodata=0)

    # GDAL Warp to Reproject
    input_vrt_33 = "Sentinel_DK_32633_8bit.vrt"
    output_vrt_33 = "Sentinel_DK_UTM33_25832_8bit.vrt"
    gdal.Warp(output_vrt_33, input_vrt_33, dstSRS="EPSG:25832", resampleAlg="cubic")

    input_vrt_32 = "Sentinel_DK_32632_8bit.vrt"
    output_vrt_32 = "Sentinel_DK_UTM32_25832_8bit.vrt"
    gdal.Warp(output_vrt_32, input_vrt_32, dstSRS="EPSG:25832", resampleAlg="cubic")

    # GDAL Build VRT with Extent
    input_vrts = [
        "Sentinel_DK_UTM33_25832_8bit.vrt",
        "Sentinel_DK_UTM32_25832_8bit.vrt"
    ]
    output_vrt = "Sentinel_DK_RGBI_8bit.vrt"

    gdal.BuildVRT(output_vrt, input_vrts, outputBounds=[400000, 6000000, 1000000, 6500000])
