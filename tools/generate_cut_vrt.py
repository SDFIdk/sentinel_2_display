from osgeo import gdal

def cut_vrt(vrt_inputs):

    utm_32_vrts = [gdal.Open(file) for file in vrt_inputs if file.startswith('32')]
    utm_33_vrts = [gdal.Open(file) for file in vrt_inputs if file.startswith('33')]

    vrt_32_8bit = "Sentinel_DK_UTM32_32632_8bit.vrt"
    vrt_33_8bit = "Sentinel_DK_UTM33_32632_8bit.vrt"

    gdal.BuildVRT(vrt_32_8bit, utm_32_vrts.read().splitlines(), srcNodata=0)
    gdal.BuildVRT(vrt_33_8bit, utm_33_vrts.read().splitlines(), srcNodata=0)

    # GDAL Warp to Reproject

    input_vrt_32 = "Sentinel_DK_32632_8bit.vrt"
    gdal.Warp(vrt_32_8bit, input_vrt_32, dstSRS="EPSG:32632", resampleAlg="cubic")
    
    input_vrt_33 = "Sentinel_DK_32633_8bit.vrt"
    gdal.Warp(vrt_33_8bit, input_vrt_33, dstSRS="EPSG:32633", resampleAlg="cubic")

    # GDAL Build VRT with Extent
    vrt_8bit = "Sentinel_DK_RGBI_8bit.vrt"
    gdal.BuildVRT(vrt_8bit, [vrt_32_8bit, vrt_33_8bit], outputBounds=[400000, 6000000, 1000000, 6500000])        

    return vrt_8bit
